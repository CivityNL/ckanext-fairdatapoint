# SPDX-FileCopyrightText: 2024 Stichting Health-RI
#
# SPDX-License-Identifier: AGPL-3.0-only

import pytest
from pytest_mock import mocker
from rdflib import Graph
from rdflib.compare import to_isomorphic
from rdflib.exceptions import ParserError

from ckanext.fairdatapoint.harvesters.domain.fair_data_point import FairDataPoint


TEST_DATA = "@prefix dcat: <http://www.w3.org/ns/dcat#> .\n"\
            "@prefix dcterms: <http://purl.org/dc/terms/> .\n" \
            "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> . \n" \
            "<https://example.com> dcterms:temporal [ a dcterms:PeriodOfTime ; \n" \
                "dcat:endDate '14-05-2023' ;\n" \
                "dcat:startDate '21-12-2021' ] .\n"\
            "<https://example.com/123> dcterms:identifier '123'^^xsd:token ."


class TestFairDataPoint:
    def test_fdp_get_graph(self, mocker):
        fdp_get_data = mocker.MagicMock(name="get_data")
        mocker.patch("ckanext.fairdatapoint.harvesters.domain.fair_data_point.FairDataPoint._get_data",
                     new=fdp_get_data)
        fdp_get_data.return_value = TEST_DATA

        expected = Graph().parse("./ckanext/fairdatapoint/tests/test_data/example_graph.ttl")
        fdp = FairDataPoint("some endpoint")
        actual = fdp.get_graph("some_path")
        assert fdp_get_data.call_count == 1
        assert to_isomorphic(actual) == to_isomorphic(expected)

    def test_fdp_get_graph_parsing_error(self, mocker):
        fdp_get_data = mocker.MagicMock(name="get_data")
        mocker.patch("ckanext.fairdatapoint.harvesters.domain.fair_data_point.FairDataPoint._get_data",
                     new=fdp_get_data)
        fdp_get_data.return_value = "I am not a graph"

        fdp = FairDataPoint("some endpoint")
        actual = fdp.get_graph("some_path")
        assert fdp_get_data.call_count == 1
        assert pytest.raises(ParserError)
        assert to_isomorphic(actual) == to_isomorphic(Graph())

    def test_fdp_get_graph_pass_empty(self, mocker):
        fdp_get_data = mocker.MagicMock(name="get_data")
        mocker.patch("ckanext.fairdatapoint.harvesters.domain.fair_data_point.FairDataPoint._get_data",
                     new=fdp_get_data)
        fdp_get_data.return_value = ""

        fdp = FairDataPoint("some endpoint")
        actual = fdp.get_graph("some_path")
        assert fdp_get_data.call_count == 1
        assert to_isomorphic(actual) == to_isomorphic(Graph())

    # @pytest.mark.xpassed(raises=ValueError)
    def test_fdp_get_graph_pass_none(self, mocker):
        fdp_get_data = mocker.MagicMock(name="get_data")
        mocker.patch("ckanext.fairdatapoint.harvesters.domain.fair_data_point.FairDataPoint._get_data",
                     new=fdp_get_data)
        fdp_get_data.return_value = None
        fdp = FairDataPoint("some endpoint")
        actual = fdp.get_graph("some_path")
        assert fdp_get_data.call_count == 1
        assert to_isomorphic(actual) == to_isomorphic(Graph())
