import logging

from ckanext.civity.harvesters.domain.record_provider import IRecordProvider
from ckanext.civity.harvesters.domain.record_provider import RecordProviderException

from ckanext.fairdatapoint.harvesters.domain.fair_data_point import FairDataPoint

from rdflib import Namespace, URIRef
from rdflib.namespace import RDF

SEPARATOR = '|'
KEY_VALUE_SEPARATOR = '_'

log = logging.getLogger(__name__)


class FairDataPointRecordProviderException(RecordProviderException):
    pass


class FairDataPointRecordProvider(IRecordProvider):
    dcat = Namespace('http://www.w3.org/ns/dcat#')
    ldp = Namespace('http://www.w3.org/ns/ldp#')

    def __init__(self, fdp_end_point):
        IRecordProvider.__init__(self)
        self.fair_data_point = FairDataPoint(fdp_end_point)

    def get_record_ids(self):
        """
        Return all the FDP records which should end up as packages in CKAN to populate the "guids_in_harvest" list
        https://rdflib.readthedocs.io/en/stable/intro_to_parsing.html
        """
        log.debug('FAIR Data Point get_records from {}'.format(self.fair_data_point.fdp_end_point))

        result = dict()

        catalogs_graph = self.fair_data_point.get_graph("/page/catalog")

        for catalog_subject in catalogs_graph.subjects(RDF.type, self.dcat.Catalog):
            catalog_id = catalog_subject.replace(self.fair_data_point.fdp_end_point + '/catalog/', '')
            result['catalog' + KEY_VALUE_SEPARATOR + catalog_id] = catalog_subject

            catalog_graph = self.fair_data_point.get_graph('/catalog/' + catalog_id)
            dataset_predicate = URIRef('http://www.w3.org/ns/dcat#dataset')
            for dataset_uri in catalog_graph.objects(predicate=dataset_predicate):
                dataset_id = dataset_uri.replace(self.fair_data_point.fdp_end_point + '/dataset/', '')
                result[
                    'catalog' + KEY_VALUE_SEPARATOR + catalog_id + SEPARATOR +
                    'dataset' + KEY_VALUE_SEPARATOR + dataset_id
                    ] = dataset_uri

                dataset_graph = self.fair_data_point.get_graph('/dataset/' + dataset_id)
                distribution_predicate = URIRef('http://www.w3.org/ns/dcat#distribution')
                for distribution_uri in dataset_graph.objects(predicate=distribution_predicate):
                    distribution_id = distribution_uri.replace(self.fair_data_point.fdp_end_point + '/distribution/', '')
                    result[
                        'catalog' + KEY_VALUE_SEPARATOR + catalog_id + SEPARATOR +
                        'dataset' + KEY_VALUE_SEPARATOR + dataset_id + SEPARATOR +
                        'distribution' + KEY_VALUE_SEPARATOR + dataset_id + SEPARATOR
                        ] = distribution_uri

        return result.keys()

    def get_record_by_id(self, guid):
        """
        Get additional information for FDP record.
        """
        log.debug('FAIR data point get_record_by_id from {} for {}'.format(self.fair_data_point.fdp_end_point, guid))

        key_values = guid.split(SEPARATOR)
        if len(key_values) > 0:
            # Get the last one, that's the one we are interested in
            key_value = key_values[len(key_values) - 1].split(KEY_VALUE_SEPARATOR)
            if len(key_value) == 2:
                result = self.fair_data_point.get_data('/' + key_value[0] + '/' + key_value[1])
                # g = self.fair_data_point.get_graph('/' + key_value[0] + '/' + key_value[1])
                # self.fair_data_point.print_graph(g)
            else:
                raise FairDataPointRecordProviderException(
                    'Unexpected number of parts in key_value [{}]: [{}]',
                    key_values[1],
                    len(key_value)
                )
        else:
            raise FairDataPointRecordProviderException(
                'Unexpected number of parts in record identifier [{}]: [{}]',
                guid,
                len(key_values)
            )

        return result
