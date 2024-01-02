import pytest
from pytest_mock import class_mocker, mocker
from rdflib import Graph, URIRef
from ckanext.fairdatapoint.harvesters.domain.fair_data_point_record_provider import FairDataPointRecordProvider


TEST_CAT_IDS_DICT = {
            "catalog=https://fair.healthinformationportal.eu/catalog/1c75c2c9-d2cc-44cb-aaa8-cf8c11515c8d":
                URIRef("https://fair.healthinformationportal.eu/catalog/1c75c2c9-d2cc-44cb-aaa8-cf8c11515c8d"),
            "catalog=https://fair.healthinformationportal.eu/catalog/1c75c2c9-d2cc-44cb-aaa8-cf8c11515c8d;"
            "dataset=https://fair.healthinformationportal.eu/dataset/898ca4b8-197b-4d40-bc81-d9cd88197670":
                URIRef("https://fair.healthinformationportal.eu/dataset/898ca4b8-197b-4d40-bc81-d9cd88197670"),
            "catalog=https://fair.healthinformationportal.eu/catalog/14225c50-00b0-4fba-8300-a677ab0c86f4":
                URIRef("https://fair.healthinformationportal.eu/catalog/14225c50-00b0-4fba-8300-a677ab0c86f4"),
            "catalog=https://fair.healthinformationportal.eu/catalog/14225c50-00b0-4fba-8300-a677ab0c86f4;"
            "dataset=https://fair.healthinformationportal.eu/dataset/32bd0246-b731-480a-b5f4-a2f60ccaebc9":
                URIRef("https://fair.healthinformationportal.eu/dataset/32bd0246-b731-480a-b5f4-a2f60ccaebc9"),
            "catalog=https://fair.healthinformationportal.eu/catalog/17412bc2-daf1-491e-94fb-6680f7a67b1e":
                URIRef("https://fair.healthinformationportal.eu/catalog/17412bc2-daf1-491e-94fb-6680f7a67b1e")
        }


def get_graph_by_id(*args, **kwargs):
    file_id = args[0]
    file_id = "_".join(file_id.split("/")[-2:])
    path_to_file = f"./ckanext-fairdatapoint/ckanext/fairdatapoint/tests/test_data/{file_id}.ttl"
    graph = Graph().parse(path_to_file)
    return graph


class TestRecordProvider:
    fdp_record_provider = FairDataPointRecordProvider("http://test_end_point.com")

    @pytest.mark.parametrize("fdp_response_file,expected",
                         [
                             ("./ckanext/fairdatapoint/tests/test_data/root_fdp_response.ttl", TEST_CAT_IDS_DICT.keys()),
                             ("./ckanext/fairdatapoint/tests/test_data/root_fdp_response_no_catalogs.ttl",
                              dict().keys())
                          ])
    def test_get_record_ids(self, mocker, fdp_response_file, expected):
        fdp_get_graph = mocker.MagicMock(name="get_data")
        mocker.patch("ckanext.fairdatapoint.harvesters.domain.fair_data_point.FairDataPoint.get_graph",
                     new=fdp_get_graph)
        fdp_get_graph.return_value = Graph().parse(fdp_response_file)
        with mocker.patch.object(FairDataPointRecordProvider, "_process_catalog", return_value=TEST_CAT_IDS_DICT):
            actual = self.fdp_record_provider.get_record_ids()
            assert actual == expected

    @pytest.mark.xfail(raises=AttributeError("'NoneType' object has no attribute 'objects'"))
    def test_get_record_ids_pass_none(self, mocker):
        with pytest.raises(AttributeError, match="'NoneType' object has no attribute 'objects'"):
            fdp_get_graph = mocker.MagicMock(name="get_data")
            mocker.patch("ckanext.fairdatapoint.harvesters.domain.fair_data_point.FairDataPoint.get_graph",
                         new=fdp_get_graph)
            fdp_get_graph.return_value = None
            self.fdp_record_provider.get_record_ids()

    def test_get_record_by_id(self, mocker):
        """A dataset with no distributions"""
        fdp_get_graph = mocker.MagicMock(name="get_data")
        mocker.patch("ckanext.fairdatapoint.harvesters.domain.fair_data_point.FairDataPoint.get_graph",
                     new=fdp_get_graph)
        guid = ("catalog=https://fair.healthinformationportal.eu/catalog/1c75c2c9-d2cc-44cb-aaa8-cf8c11515c8d;"
                "dataset=https://fair.healthinformationportal.eu/dataset/898ca4b8-197b-4d40-bc81-d9cd88197670")
        fdp_get_graph.side_effect = get_graph_by_id
        actual = self.fdp_record_provider.get_record_by_id(guid)
        expected = Graph().parse(f"./ckanext-fairdatapoint/ckanext/fairdatapoint/tests/test_data/dataset_898ca4b8-197b-4d40-bc81-d9cd88197670.ttl").serialize()
        assert actual == expected

    def test_get_record_by_id_distr(self, mocker):
        """A dataset with a distribution, title, description, licence, format and accessURL are added to dataset info"""
        fdp_get_graph = mocker.MagicMock(name="get_data")
        mocker.patch("ckanext.fairdatapoint.harvesters.domain.fair_data_point.FairDataPoint.get_graph",
                     new=fdp_get_graph)
        guid = ("catalog=https://health-ri.sandbox.semlab-leiden.nl/catalog/e3faf7ad-050c-475f-8ce4-da7e2faa5cd0;"
                "dataset=https://health-ri.sandbox.semlab-leiden.nl/dataset/d7129d28-b72a-437f-8db0-4f0258dd3c25")
        fdp_get_graph.side_effect = get_graph_by_id
        actual = self.fdp_record_provider.get_record_by_id(guid)
        expected = Graph().parse(f"./ckanext-fairdatapoint/ckanext/fairdatapoint/tests/test_data/dataset_d7129d28-b72a-437f-8db0-4f0258dd3c25_out.ttl").serialize()
        assert actual == expected
