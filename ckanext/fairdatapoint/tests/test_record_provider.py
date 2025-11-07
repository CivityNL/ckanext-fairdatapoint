# SPDX-FileCopyrightText: 2024 Stichting Health-RI
#
# SPDX-License-Identifier: AGPL-3.0-only

from pathlib import Path

import pytest
import requests_mock
from pytest_mock import class_mocker, mocker
from rdflib import Graph, URIRef

from ckanext.fairdatapoint.harvesters.domain.fair_data_point_record_provider import (
    FairDataPointRecordProvider,
)

TEST_DATA_DIRECTORY = Path(Path(__file__).parent.resolve(), "test_data")


def get_graph_by_id(*args, **kwargs):
    file_id = args[0]
    file_id = "_".join(file_id.split("/")[-2:])
    path_to_file = Path(TEST_DATA_DIRECTORY, f"{file_id}.ttl")
    graph = Graph().parse(path_to_file)
    return graph


class TestRecordProvider:
    fdp_record_provider = FairDataPointRecordProvider("http://test_end_point.com")

    @pytest.mark.parametrize(
        "fdp_response_file,expected",
        [
            (
                    Path(TEST_DATA_DIRECTORY, "root_fdp_response.ttl"),
                    {
                        'dataseries=http://example.org/DatasetSeries1', 'dataset=http://example.org/Dataset1'
                    }
            ),
            (
                    Path(TEST_DATA_DIRECTORY, "root_fdp_response_no_catalogs.ttl"),
                    set()
            ),
        ],
    )
    def test_get_record_ids(self, mocker, fdp_response_file, expected):
        fdp_get_graph = mocker.MagicMock(name="get_data")
        mocker.patch(
            "ckanext.fairdatapoint.harvesters.domain.fair_data_point.FairDataPoint.get_graph",
            new=fdp_get_graph,
        )
        fdp_get_graph.return_value = Graph().parse(fdp_response_file)

        actual = self.fdp_record_provider.get_record_ids()

        actual = set(actual)

        assert actual == expected

    @pytest.mark.parametrize(
        "fdp_response_file,expected",
        [
            (
                    Path(TEST_DATA_DIRECTORY, "fdp_multiple_parents.ttl"),
                    {
                        'dataseries=http://example.org/Dataseries1',
                        'dataset=http://example.org/Dataset1'
                    },
            )
        ],
    )
    def test_get_record_ids_multiple_parents(self, mocker, fdp_response_file, expected):
        fdp_get_graph = mocker.MagicMock(name="get_data")
        mocker.patch(
            "ckanext.fairdatapoint.harvesters.domain.fair_data_point.FairDataPoint.get_graph",
            new=fdp_get_graph,
        )
        fdp_get_graph.return_value = Graph().parse(fdp_response_file)
        actual = self.fdp_record_provider.get_record_ids()

        actual = set(actual)
        assert actual == expected

    @pytest.mark.parametrize(
        "harvest_catalogs, expected_keys",
        [
            (
                    False,
                    {
                        'dataset=http://example.com/dataset1'
                    },
            ),
            (
                    True,
                    {
                        'dataset=http://example.com/dataset1',
                        'catalog=http://example.com/catalog1'
                    }
            ),
        ],
    )
    def test_get_record_ids_configuration_harvest_catalogs(self, mocker, harvest_catalogs, expected_keys):
        """Test whether the harvest_catalogs setting affects the processing of catalogs correctly."""

        fdp_get_graph = mocker.MagicMock(name="get_data")
        mocker.patch(
            "ckanext.fairdatapoint.harvesters.domain.fair_data_point.FairDataPoint.get_graph",
            new=fdp_get_graph,
        )
        fdp_get_graph.return_value = Graph().parse(
            Path(TEST_DATA_DIRECTORY, "fdp_process_catalogs.ttl")
        )

        self.fdp_record_provider.harvest_catalogs = harvest_catalogs
        actual_result = self.fdp_record_provider.get_record_ids()

        actual_keys = set(actual_result)
        # Assertions
        assert actual_keys == expected_keys

    def test_get_record_ids_pass_none(self, mocker):
        with pytest.raises(
                ValueError, match="rdf_graph cannot be None"):
            fdp_get_graph = mocker.MagicMock(name="get_data")
            mocker.patch(
                "ckanext.fairdatapoint.harvesters.domain.fair_data_point.FairDataPoint.get_graph",
                new=fdp_get_graph,
            )
            fdp_get_graph.return_value = None
            self.fdp_record_provider.get_record_ids()

    def test_get_record_by_id(self, mocker):
        """A dataset with no distributions"""
        fdp_get_graph = mocker.MagicMock(name="get_data")
        mocker.patch(
            "ckanext.fairdatapoint.harvesters.domain.fair_data_point.FairDataPoint.get_graph",
            new=fdp_get_graph,
        )
        guid = (
            "catalog=https://fair.healthinformationportal.eu/catalog/1c75c2c9-d2cc-44cb-aaa8-cf8c11515c8d;"
            "dataset=https://fair.healthinformationportal.eu/dataset/898ca4b8-197b-4d40-bc81-d9cd88197670"
        )
        fdp_get_graph.side_effect = get_graph_by_id
        actual = self.fdp_record_provider.get_record_by_id(guid)
        expected = (
            Graph()
            .parse(
                Path(
                    TEST_DATA_DIRECTORY,
                    "dataset_898ca4b8-197b-4d40-bc81-d9cd88197670.ttl",
                )
            )
            .serialize()
        )
        assert actual == expected

    def test_get_record_by_id_distr(self, mocker):
        """A dataset with a distribution, title, description, licence, format and accessURL are added to dataset info"""
        fdp_get_graph = mocker.MagicMock(name="get_data")
        mocker.patch(
            "ckanext.fairdatapoint.harvesters.domain.fair_data_point.FairDataPoint.get_graph",
            new=fdp_get_graph,
        )
        guid = (
            "catalog=https://health-ri.sandbox.semlab-leiden.nl/catalog/e3faf7ad-050c-475f-8ce4-da7e2faa5cd0;"
            "dataset=https://health-ri.sandbox.semlab-leiden.nl/dataset/d7129d28-b72a-437f-8db0-4f0258dd3c25"
        )
        fdp_get_graph.side_effect = get_graph_by_id
        actual = self.fdp_record_provider.get_record_by_id(guid)
        expected = (
            Graph()
            .parse(
                Path(
                    TEST_DATA_DIRECTORY,
                    "dataset_d7129d28-b72a-437f-8db0-4f0258dd3c25_out.ttl",
                )
            )
            .serialize()
        )
        assert actual == expected

    def test_orcid_call(self, mocker):
        """if orcid url in contact point - add vcard full name"""
        with requests_mock.Mocker() as mock:
            mock.get(
                "https://orcid.org/0000-0002-4348-707X/public-record.json",
                json={"displayName": "N.K. De Vries"},
            )
            fdp_get_graph = mocker.MagicMock(name="get_data")
            mocker.patch(
                "ckanext.fairdatapoint.harvesters.domain.fair_data_point.FairDataPoint.get_graph",
                new=fdp_get_graph,
            )
            guid = (
                "catalog=https://covid19initiatives.health-ri.nl/p/ProjectOverview?focusarea="
                "http://purl.org/zonmw/generic/10006;"
                "dataset=https://covid19initiatives.health-ri.nl/p/Project/27866022694497978"
            )
            fdp_get_graph.side_effect = get_graph_by_id
            actual = self.fdp_record_provider.get_record_by_id(guid)
            expected = (
                Graph()
                .parse(Path(TEST_DATA_DIRECTORY, "Project_27866022694497978_out.ttl"))
                .serialize()
            )
            assert mock.called
            assert actual == expected
