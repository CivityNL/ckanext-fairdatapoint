import pytest
from unittest.mock import patch
from rdflib import Graph
from ckanext.fairdatapoint.harvesters.domain.fair_data_point_record_to_package_converter import (
    FairDataPointRecordToPackageConverter)


@pytest.mark.ckan_config("ckan.plugins", "scheming_datasets")
@pytest.mark.usefixtures("with_plugins")
class TestProcessors:
    @patch("ckanext.fairdatapoint.processors.FairDataPointRDFParser.datasets")
    def test_fdp_record_converter_dataset(self, parser_datasets):
        fdp_record_to_package = FairDataPointRecordToPackageConverter(profile="fairdatapoint_dcat_ap")
        data = Graph().parse("./ckanext-fairdatapoint/ckanext/fairdatapoint/tests/test_data/"
                             "Project_27866022694497978_out.ttl").serialize()
        fdp_record_to_package.record_to_package(guid="catalog=https://covid19initiatives.health-ri.nl/p/"
                                                     "ProjectOverview?focusarea=http://purl.org/zonmw/generic/10006;"
                                                     "dataset=https://covid19initiatives.health-ri.nl/p/Project/"
                                                     "27866022694497978",
                                                record=data)
        assert parser_datasets.called

    @patch("ckanext.fairdatapoint.processors.FairDataPointRDFParser.catalogs")
    def test_fdp_record_converter_catalog(self, parser_catalogs):
        fdp_record_to_package = FairDataPointRecordToPackageConverter(profile="fairdatapoint_dcat_ap")
        data = Graph().parse(
            "./ckanext-fairdatapoint/ckanext/fairdatapoint/tests/test_data/fdp_catalog.ttl").serialize()
        fdp_record_to_package.record_to_package(
            guid="catalog=https://fair.healthinformationportal.eu/catalog/1c75c2c9-d2cc-44cb-aaa8-cf8c11515c8d",
            record=data)
        assert parser_catalogs.called

    def test_fdp_record_converter_dataset_dict(self):
        fdp_record_to_package = FairDataPointRecordToPackageConverter(profile="fairdatapoint_dcat_ap")
        data = Graph().parse("./ckanext-fairdatapoint/ckanext/fairdatapoint/tests/test_data/"
                             "Project_27866022694497978_out.ttl").serialize()
        actual_dataset = fdp_record_to_package.record_to_package(
            guid="catalog=https://covid19initiatives.health-ri.nl/p/ProjectOverview?focusarea="
                 "http://purl.org/zonmw/generic/10006;"
                 "dataset=https://covid19initiatives.health-ri.nl/p/Project/27866022694497978",
            record=data)
        expected_dataset = {"extras":
            [
                {"key": "uri", "value": "https://covid19initiatives.health-ri.nl/p/Project/27866022694497978"},
                {"key": "hello",
                 "value": "Hello from the FAIR data point profile. Use this function to do FAIR data point "
                          "specific stuff during the import stage"}
            ],
            "resources": [],
            "title": "COVID-NL cohort MUMC+",
            "notes": "Clinical data of MUMC COVID-NL cohort",
            "tags": [],
            "license_id": "",
            "identifier": "27866022694497978",
            "has_version": ["https://repo.metadatacenter.org/template-instances/2836bf1c-76e9-44e7-a65e-80e9ca63025a"],
            "contact_uri": "https://orcid.org/0000-0002-4348-707X",
            "publisher_uri": "https://opal.health-ri.nl/pub/",
            "temporal_start": "2020-01-01",
            "temporal_end": "2025-12-31"}
        assert actual_dataset == expected_dataset

    def test_fdp_record_converter_catalog_dict(self):
        fdp_record_to_package = FairDataPointRecordToPackageConverter(profile="fairdatapoint_dcat_ap")
        data = Graph().parse(
            "./ckanext-fairdatapoint/ckanext/fairdatapoint/tests/test_data/fdp_catalog.ttl").serialize()
        actual = fdp_record_to_package.record_to_package(
            guid="catalog=https://fair.healthinformationportal.eu/catalog/1c75c2c9-d2cc-44cb-aaa8-cf8c11515c8d",
            record=data)
        expected = {
                       "access_rights": "https://fair.healthinformationportal.eu/catalog/"
                                        "1c75c2c9-d2cc-44cb-aaa8-cf8c11515c8d#accessRights",
                       "conforms_to": ["https://fair.healthinformationportal.eu/profile/"
                                      "a0949e72-4466-4d53-8900-9436d1049a4b"],
                       "extras": [{"key": "uri",
                                   "value": "https://fair.healthinformationportal.eu/catalog/"
                                            "1c75c2c9-d2cc-44cb-aaa8-cf8c11515c8d"},
                                  {"key": "hello",
                                   "value": "Hello from the FAIR data point profile. Use this "
                                            "function to do FAIR data point specific stuff during "
                                            "the import stage"}],
                       "has_version": ["1.0"],
                       "issued": "2023-10-06T10:12:55.614000+00:00",
                       "language": ["http://id.loc.gov/vocabulary/iso639-1/en"],
                       "license_id": "",
                       "modified": "2023-10-06T10:12:55.614000+00:00",
                       "publisher_name": "Automatic",
                       "resources": [],
                       "tags": [],
                       "title": "Slovenia National Node"
        }
        assert actual == expected
