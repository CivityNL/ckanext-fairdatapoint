# SPDX-FileCopyrightText: 2023 Civity
# SPDX-FileContributor: 2024 Stichting Health-RI
#
# SPDX-License-Identifier: AGPL-3.0-only

import cgitb
import json
import logging
import sys
import uuid
import warnings
from abc import abstractmethod

import ckan.plugins.toolkit as toolkit
from ckan import model

from ckanext.fairdatapoint.harvesters.domain.identifier import Identifier
from ckanext.harvest.harvesters import HarvesterBase
from ckanext.harvest.model import HarvestObject
from ckanext.harvest.model import HarvestObjectExtra as HOExtra

ID = "id"

log = logging.getLogger(__name__)

RESOLVE_LABELS = "resolve_labels"

def text_traceback():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        res = "the original traceback:".join(
            cgitb.text(sys.exc_info()).split("the original traceback:")[1:]
        ).strip()
    return res


class CivityHarvesterException(Exception):
    pass


class CivityHarvester(HarvesterBase):
    """
    A Harvester base class for multiple Civity harvesters. This class contains the harvester bookkeeping and delegates
    the harvester specific work to a RecordProvider (to access records from a harvest source) and a
    RecordToPackageConverter to convert proprietary data from the harvest source to CKAN packages.
    """

    record_provider = None

    record_to_package_converter = None

    @abstractmethod
    def setup_record_provider(self, harvest_url, harvest_config_dict):
        pass

    @abstractmethod
    def setup_record_to_package_converter(self, harvest_url, harvest_config_dict):
        pass

    def gather_stage(self, harvest_job):
        """
        The gather stage will receive a HarvestJob object and will be
        responsible for:
            - gathering all the necessary objects to fetch on a later.
              stage (e.g. for a CSW server, perform a GetRecords request)
            - creating the necessary HarvestObjects in the database, specifying
              the guid and a reference to its job. The HarvestObjects need a
              reference date with the last modified date for the resource, this
              may need to be set in a different stage depending on the type of
              source.
            - creating and storing any suitable HarvestGatherErrors that may
              occur.
            - returning a list with all the ids of the created HarvestObjects.
            - to abort the harvest, create a HarvestGatherError and raise an
              exception. Any created HarvestObjects will be deleted.

        :param harvest_job: HarvestJob object
        :returns: A list of HarvestObject ids
        """

        logger = logging.getLogger(__name__ + ".gather_stage")

        logger.debug("Starting gather_stage for job: [%r]", harvest_job)

        #
        result = []

        self.setup_record_provider(
            harvest_job.source.url, self._get_harvest_config(harvest_job.source.config)
        )

        guids_to_package_ids = self._get_guids_to_package_ids_from_database(harvest_job)

        guids_in_db = set(guids_to_package_ids.keys())

        guids_in_harvest = self._get_guids_in_harvest(harvest_job)
        if guids_in_harvest:
            # Sort so that dataseries are processed before datasets
            guids_in_harvest = sorted(
                guids_in_harvest,
                key=lambda g: 0 if "dataseries=" in g else 1
            )

            guids_in_harvest_set = set(guids_in_harvest)

            new = guids_in_harvest_set - guids_in_db
            delete = guids_in_db - guids_in_harvest_set
            change = guids_in_db & guids_in_harvest_set

            for guid in new:
                existing = (
                    model.Session.query(HarvestObject)
                    .filter_by(guid=guid, harvest_source_id=harvest_job.source.id, harvest_job_id=harvest_job.id)
                    .first())
                if not existing:
                    obj = HarvestObject(
                        guid=guid,
                        job=harvest_job,
                        extras=[HOExtra(key="status", value="new")],
                    )
                    obj.save()
                    result.append(obj.id)
                else:
                    logger.info(
                        "Duplicate HarvestObject for guid [%s] and source [%s] already exists. Skipping.",
                        guid, harvest_job.source.id
                    )
            for guid in change:
                obj = HarvestObject(
                    guid=guid,
                    job=harvest_job,
                    package_id=guids_to_package_ids[guid],
                    extras=[HOExtra(key="status", value="change")],
                )
                obj.save()
                result.append(obj.id)
            for guid in delete:
                obj = HarvestObject(
                    guid=guid,
                    job=harvest_job,
                    package_id=guids_to_package_ids[guid],
                    extras=[HOExtra(key="status", value="delete")],
                )
                # TODO
                #  Deleted object is marked as not being current here already. When the actual deletion of the package
                #  fails in the import stage, an orphan package will remain in existence and never be deleted.
                model.Session.query(HarvestObject).filter_by(guid=guid).update(
                    {"current": False}, False
                )
                obj.save()
                result.append(obj.id)

        # Why is this needed? An empty list seems a valid result of this stage. There is simply nothing to do
        # if len(result) == 0:
        #     result = None

        logger.debug("Finished gather_stage for job: [%r]", harvest_job)

        return result

    def fetch_stage(self, harvest_object):
        """
        The fetch stage will receive a HarvestObject object and will be
        responsible for:
            - getting the contents of the remote object (e.g. for a CSW server,
              perform a GetRecordById request).
            - saving the content in the provided HarvestObject.
            - creating and storing any suitable HarvestObjectErrors that may
              occur.
            - returning True if everything is ok (ie the object should now be
              imported), "unchanged" if the object didn't need harvesting after
              all (ie no error, but don't continue to import stage) or False if
              there were errors.

        :param harvest_object: HarvestObject object
        :returns: True if successful, 'unchanged' if nothing to import after
                  all, False if not successful
        """

        logger = logging.getLogger(__name__ + ".fetch_stage")

        logger.debug("Starting fetch_stage for harvest object [%s]", harvest_object.id)

        self.setup_record_provider(
            harvest_object.source.url,
            self._get_harvest_config(harvest_object.source.config),
        )

        # Check harvest object status
        status = self._get_object_extra(harvest_object, "status")

        if status == "delete":
            # No need to fetch anything, just pass to the import stage
            result = True

        else:
            identifier = harvest_object.guid
            try:
                record = self.record_provider.get_record_by_id(identifier)

                if record:
                    try:
                        # Save the fetch contents in the HarvestObject
                        harvest_object.content = record  # TODO move JSON stuff to record provider for Gisweb harvester
                        harvest_object.save()
                    except Exception as e:
                        self._save_object_error(
                            "Error saving harvest object for identifier [%s] [%r]"
                            % (identifier, e),
                            harvest_object,
                        )
                        return False

                    model.Session.commit()

                    logger.debug(
                        "Record content saved for ID [%s], harvest object ID [%s]",
                        harvest_object.guid,
                        harvest_object.id,
                    )

                    result = True
                else:
                    self._save_object_error(
                        "Empty record for identifier %s" % identifier, harvest_object
                    )
                    result = False

            except (
                Exception
            ) as e:  # Broad exception because of unpredictability of Exceptions
                self._save_object_error(
                    "Error getting the record with identifier [%s] from record provider"
                    % identifier,
                    harvest_object,
                )
                result = False

        logger.debug("Finished fetch_stage for harvest object [%s]", harvest_object.id)

        return result

    def import_stage(self, harvest_object):
        """
        The import stage will receive a HarvestObject object and will be
        responsible for:
            - performing any necessary action with the fetched object (e.g.
              create, update or delete a CKAN package).
              Note: if this stage creates or updates a package, a reference
              to the package should be added to the HarvestObject.
            - setting the HarvestObject.package (if there is one)
            - setting the HarvestObject.current for this harvest:
               - True if successfully created/updated
               - False if successfully deleted
            - setting HarvestObject.current to False for previous harvest
              objects of this harvest source if the action was successful.
            - creating and storing any suitable HarvestObjectErrors that may
              occur.
            - creating the HarvestObject - Package relation (if necessary)
            - returning True if the action was done, "unchanged" if the object
              didn't need harvesting after all or False if there were errors.

        NB You can run this stage repeatedly using 'paster harvest import'.

        :param harvest_object: HarvestObject object
        :returns: True if the action was done, "unchanged" if the object didn't
                  need harvesting after all or False if there were errors.
        """

        logger = logging.getLogger(__name__ + ".import_stage")

        logger.debug("Starting import stage for harvest_object [%s]", harvest_object.id)

        self.setup_record_to_package_converter(
            harvest_object.source.url,
            self._get_harvest_config(harvest_object.source.config),
        )

        status = self._get_object_extra(harvest_object, "status")

        if status == "delete":
            # Delete package
            context = {
                "model": model,
                "session": model.Session,
                "user": self._get_user_name(),
            }

            toolkit.get_action("package_delete")(
                context, {ID: harvest_object.package_id}
            )
            logger.info(
                "Deleted package {0} with guid {1}".format(
                    harvest_object.package_id, harvest_object.guid
                )
            )

            return True

        if harvest_object.content is None:
            self._save_object_error(
                "Empty content for object %s" % harvest_object.id,
                harvest_object,
                "Import",
            )
            return False

        try:
            # Determine datatype
            identifier_harvest_object = Identifier(harvest_object.guid)
            datatype = identifier_harvest_object.get_id_type()

            if datatype == "dataset":
                # Build mapping from dataseries GUID to package ID for all active dataset_series in the database
                series_results = model.Session.query(model.PackageExtra.value, model.Package.id) \
                    .join(model.Package) \
                    .filter(model.PackageExtra.key == 'guid') \
                    .filter(model.Package.type == 'dataset_series') \
                    .filter(model.Package.state == 'active') \
                    .all()
                series_mapping = {guid: {"id": series_id} for guid, series_id in series_results}
                package_dict = self.record_to_package_converter.record_to_package(
                    harvest_object.guid, str(harvest_object.content), series_mapping=series_mapping
                )
            else:
                package_dict = self.record_to_package_converter.record_to_package(
                    harvest_object.guid, str(harvest_object.content)
                )
            package_dict.setdefault("extras", []).append({"key": "guid", "value": identifier_harvest_object.get_id_value()})
        except Exception as e:
            logger.error(
                "Error converting record to package for identifier [%s] [%r]"
                % (harvest_object.id, e)
            )
            self._save_object_error(
                "Error converting record to package for identifier [%s] [%r]"
                % (harvest_object.id, e),
                harvest_object,
            )
            return False

        if not package_dict:
            return False

        # TODO Doesn't this mean a new name will be generated for each update? This should be a new which never ever
        #  changes as long as the record in the harvester source does not change
        logger.info(
            "Generating package name from title [{}]".format(package_dict["title"])
        )
        try:
            if status == "new" and "name" not in package_dict:
                try:
                    package_dict["name"] = self._gen_new_name(package_dict["title"])
                    logger.info(
                        "Generated package name from title [{}]: [{}]".format(
                            package_dict.get("title", "UNKNOWN TITLE"),
                            package_dict["name"]
                        )
                    )
                except TypeError:
                    logger.error(
                        "TypeError: error generating package name. Package title is not a string: [%s]",
                        str(package_dict.get("title"))
                    )
                    self._save_object_error(
                        "TypeError: error generating package name. Package title [%s] is not a string." %
                        str(package_dict.get("title")),
                        harvest_object,
                    )
                    return False

        except Exception as e:
            logger.exception("Unexpected error during name generation for package")
            self._save_object_error(str(e), harvest_object)
            return False


        # Fallback: ensure name is always set
        if "name" not in package_dict:
            package_dict["name"] = self._gen_new_name(package_dict["title"])


        # Unless already set by an extension, get the owner organization (if any)
        # from the harvest source dataset
        if not package_dict.get("owner_org"):
            source_dataset = model.Package.get(harvest_object.source.id)
            if source_dataset.owner_org:
                package_dict["owner_org"] = source_dataset.owner_org

        context = {
            "user": self._get_user_name(),
            "return_id_only": True,
            "ignore_auth": True,
        }

        # Variable for the new or existing package ID
        package_id = None

        # Separate Update of package and resources, for trigger reasons
        resources = package_dict.pop("resources")

        if status == "new":
            # If a package ID has not been assigned by the RecordToPackageConverter...
            if ID not in package_dict.keys():
                # ... we need to explicitly provide a new package ID.
                package_dict[ID] = str(uuid.uuid4())

            # Save reference to the package on the object
            harvest_object.package_id = package_dict[ID]
            harvest_object.current = True
            harvest_object.add()

            # Now safely defer and flush
            model.Session.execute(
                "SET CONSTRAINTS harvest_object_package_id_fkey DEFERRED"
            )
            model.Session.flush()

            # Create the package in CKAN
            package_id = self._create_or_update_package(
                package_dict, "create", context, harvest_object
            )

        elif status == "change":
            # Updating existing package, if all is well...
            package_dict[ID] = harvest_object.package_id

            # Update existing package
            package_id = self._create_or_update_package(
                package_dict, "update", context, harvest_object
            )

        # In case of success (package_id is defined in that case), create the resources
        if package_id:
            if not self._create_resources(
                resources, package_id, package_dict["title"], context, harvest_object
            ):
                return False
        else:
            return False

        # 🔧 Clear previous current HarvestObjects with the same GUID
        model.Session.query(HarvestObject).filter(
            HarvestObject.guid == harvest_object.guid,
            HarvestObject.current == True,
            HarvestObject.id != harvest_object.id
        ).update({"current": False}, synchronize_session=False)

        # ✅ Mark this object as current
        harvest_object.current = True
        harvest_object.add()

        model.Session.commit()

        logger.debug("Finished import stage for harvest_object [%s]", harvest_object.id)
        return True


    def _create_or_update_package(
        self, package_dict, create_or_update, context, harvest_object
    ):
        if "revision_id" in package_dict.keys():
            package_dict.pop("revision_id")

        try:
            action = "package_" + create_or_update
            result = toolkit.get_action(action)(context.copy(), package_dict)
            log.info(
                "Successful [%s] for package with id [%s]", create_or_update, result
            )
        except toolkit.ValidationError as e:
            error_message = "Error in [{}] for package [{}]: [{}]".format(
                create_or_update, package_dict["title"], e
            )
            log.error(error_message)
            self._save_object_error(error_message, harvest_object)
            result = None

        return result

    def _create_resources(
        self, resource_dicts, package_id, package_title, context, harvest_object
    ):
        result = True

        for resource_dict in resource_dicts:
            if "id" in resource_dict.keys():
                resource_dict.pop("id")

            if "revision_id" in resource_dict.keys():
                resource_dict.pop("revision_id")

            resource_dict["package_id"] = package_id
            try:
                resource_dict = toolkit.get_action("resource_create")(
                    context.copy(), resource_dict
                )
                log.info(
                    "Created resource with id [%s]",
                    resource_dict.get("id", "NO ID Found"),
                )
            except toolkit.ValidationError as e:
                log.error("Error creating resource: [%s]", e.message)
                self._save_object_error(
                    "Error creating resource [%s] for identifier [%s] [%r]"
                    % (package_title, harvest_object.id, e),
                    harvest_object,
                )
                result = False

        return result

    @staticmethod
    def _get_guids_to_package_ids_from_database(harvest_job):
        """
        Read from GUID's and associated package ID's as currently present from database to be able to create
        the three to do lists
        :param harvest_job:
        :return:
        """
        query = (
            model.Session.query(HarvestObject.guid, HarvestObject.package_id)
            .filter(HarvestObject.current == True)
            .filter(HarvestObject.harvest_source_id == harvest_job.source.id)
        )

        guid_to_package_id = {}

        for guid, package_id in query:
            guid_to_package_id[guid] = package_id

        return guid_to_package_id

    def _get_guids_in_harvest(self, harvest_job):
        """
        Get identifiers of records in harvest source. These should be present in CKAN once all imports have
        finished.
        :param harvest_job:
        :return:
        """
        guids_in_harvest = set()

        try:
            for identifier in self.record_provider.get_record_ids():
                try:
                    log.info("Got identifier [%s] from RecordProvider", identifier)
                    if identifier is None:
                        log.error(
                            "RecordProvider returned empty identifier [%r], skipping..."
                            % identifier
                        )
                        continue

                    guids_in_harvest.add(identifier)
                except Exception as e:
                    self._save_gather_error(
                        "Error for identifier [%s] in gather phase: [%r]"
                        % (identifier, e),
                        harvest_job,
                    )
                    continue
        except Exception as e:
            log.error("Exception: %s" % text_traceback())
            self._save_gather_error(
                "Error gathering the identifiers from the RecordProvider: [%s]"
                % str(e),
                harvest_job,
            )
            guids_in_harvest = None

        return guids_in_harvest

    @staticmethod
    def _get_harvest_config(config_str):
        """
        Loads the source configuration JSON object into a dict for convenient access
        """
        config_dict = {}

        if config_str:
            config_dict = json.loads(config_str)

        return config_dict

    @staticmethod
    def _get_object_extra(harvest_object, key):
        """
        Helper function for retrieving the value from a harvest object extra,
        given the key
        """
        for extra in harvest_object.extras:
            if extra.key == key:
                return extra.value
        return None

    def _get_template_package_dict(self, harvest_config_dict):
        """
        Get template package dictionary. This approach has the advantage that in case someone modifies the
        schema, the harvester configuration can be left untouched without the harvester breaking. Disadvantage is
        that there is a package which should never be shown to users.
        TODO
          is this the most convenient solution? Are there better alternatives which provide the same functionality
          without the drawback of running the risk of the template showing up somewhere unexpectedly.
        :param harvest_config_dict:
        :return:
        """
        context = {
            "user": self._get_user_name(),
            "return_id_only": True,
            "ignore_auth": True,
        }

        template_package_id = self._get_template_package_id(harvest_config_dict)
        try:
            result = toolkit.get_action("package_show")(
                context.copy(), {"id": template_package_id}
            )
        except toolkit.ObjectNotFound as e:
            log.error(
                "Error looking up template package [%s]: [%s]",
                template_package_id,
                e.message,
            )
            result = None

        return result

    @staticmethod
    def _get_template_package_id(harvest_config_dict):
        """
        Retrieves template package ID from harvest_config dictionary key 'template_package_id_id' if it exists
        ex. {'template_package_id': 'template_for_rotterdam_dataplatform'}
        """

        if "template_package_id" in harvest_config_dict.keys():
            result = harvest_config_dict.get("template_package_id", "template")
        else:
            result = "template"

        return result

