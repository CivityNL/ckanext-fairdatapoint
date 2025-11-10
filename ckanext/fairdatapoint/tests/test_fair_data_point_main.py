# SPDX-FileCopyrightText: 2024 Stichting Health-RI
#
# SPDX-License-Identifier: AGPL-3.0-only 

from unittest.mock import patch
from ckanext.fairdatapoint.fair_data_point_main import main
from ckanext.fairdatapoint.harvesters.domain.fair_data_point_record_provider import FairDataPointRecordProvider
from rdflib import URIRef


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

TEST_NO_DATASETS_DICT = {
            "catalog=https://fair.healthinformationportal.eu/catalog/1c75c2c9-d2cc-44cb-aaa8-cf8c11515c8d":
                URIRef("https://fair.healthinformationportal.eu/catalog/1c75c2c9-d2cc-44cb-aaa8-cf8c11515c8d")}


def get_iterable_for_mock():
    return TEST_CAT_IDS_DICT.keys()


def get_no_dataset_keys():
    return TEST_NO_DATASETS_DICT.keys()


class TestFDPPlugin:
    @patch("ckanext.fairdatapoint.harvesters.domain.fair_data_point_record_provider.FairDataPointRecordProvider"
           ".get_record_ids")
    def test_main(self, get_record_ids, mocker):
        spy = mocker.spy(FairDataPointRecordProvider, "__init__")
        main()
        assert spy.call_count == 3
        expected_calls = [
            "https://fair.healthinformationportal.eu",
            "https://health-ri.sandbox.semlab-leiden.nl/",
            "https://portal-gdi-nl.molgeniscloud.org/api/fdp/"
        ]
        real_arguments = [x.args[1] for x in spy.call_args_list]
        assert spy.call_count == 3
        get_record_ids.assert_called()
        assert real_arguments == expected_calls

    @patch("ckanext.fairdatapoint.harvesters.domain.fair_data_point_record_provider.FairDataPointRecordProvider"
           ".get_record_ids")
    @patch("ckanext.fairdatapoint.harvesters.domain.fair_data_point_record_provider.FairDataPointRecordProvider"
           ".get_record_by_id")
    @patch("ckanext.fairdatapoint.harvesters.domain.fair_data_point_record_provider.FairDataPointRecordProvider"
           ".__init__")
    def test_main_get_record_by_id(self, init_fdp, get_record_by_id, get_record_ids):
        init_fdp.return_value = None
        get_record_ids.side_effect = get_iterable_for_mock
        main()
        assert get_record_by_id.call_count == 3

    @patch("ckanext.fairdatapoint.harvesters.domain.fair_data_point_record_provider.FairDataPointRecordProvider"
           ".get_record_ids")
    @patch("ckanext.fairdatapoint.harvesters.domain.fair_data_point_record_provider.FairDataPointRecordProvider"
           ".get_record_by_id")
    @patch("ckanext.fairdatapoint.harvesters.domain.fair_data_point_record_provider.FairDataPointRecordProvider"
           ".__init__")
    def test_main_get_record_by_id(self, init_fdp, get_record_by_id, get_record_ids):
        init_fdp.return_value = None
        get_record_ids.side_effect = get_no_dataset_keys
        main()
        assert get_record_by_id.call_count == 0
