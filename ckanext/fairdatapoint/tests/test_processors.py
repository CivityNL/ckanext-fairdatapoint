# SPDX-FileCopyrightText: 2024 Stichting Health-RI
#
# SPDX-License-Identifier: AGPL-3.0-only

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from rdflib import Graph
from ckanext.fairdatapoint.harvesters.domain.fair_data_point_record_to_package_converter import (
    FairDataPointRecordToPackageConverter)

TEST_DATA_DIRECTORY = Path(Path(__file__).parent.resolve(), "test_data")


@pytest.mark.ckan_config("ckan.plugins", "scheming_datasets")
@pytest.mark.usefixtures("with_plugins")
class TestProcessors:
    @patch("ckanext.fairdatapoint.processors.FairDataPointRDFParser.datasets")
    def test_fdp_record_converter_dataset(self, parser_datasets):
        fdp_record_to_package = FairDataPointRecordToPackageConverter(profile="fairdatapoint_dcat_ap")
        data = Graph().parse(Path(TEST_DATA_DIRECTORY, "Project_27866022694497978_out.ttl")).serialize()
        fdp_record_to_package.record_to_package(guid="catalog=https://covid19initiatives.health-ri.nl/p/"
                                                     "ProjectOverview?focusarea=http://purl.org/zonmw/generic/10006;"
                                                     "dataset=https://covid19initiatives.health-ri.nl/p/Project/"
                                                     "27866022694497978",
                                                record=data)
        assert parser_datasets.called

    @patch("ckanext.fairdatapoint.processors.FairDataPointRDFParser.catalogs")
    def test_fdp_record_converter_catalog(self, parser_catalogs):
        fdp_record_to_package = FairDataPointRecordToPackageConverter(profile="fairdatapoint_dcat_ap")
        data = Graph().parse(Path(TEST_DATA_DIRECTORY, "fdp_catalog.ttl")).serialize()
        fdp_record_to_package.record_to_package(
            guid="catalog=https://fair.healthinformationportal.eu/catalog/1c75c2c9-d2cc-44cb-aaa8-cf8c11515c8d",
            record=data, series_mapping=None)
        assert parser_catalogs.called

    @staticmethod
    def _extras_to_dict(extras_list):
        return {item["key"]: item["value"] for item in extras_list}

    def test_fdp_record_converter_dataset_dict(self):
        fdp_record_to_package = FairDataPointRecordToPackageConverter(profile="fairdatapoint_dcat_ap")
        data = Graph().parse(Path(TEST_DATA_DIRECTORY, "Project_27866022694497978_out.ttl")).serialize()
        actual_dataset = fdp_record_to_package.record_to_package(
            guid="catalog=https://covid19initiatives.health-ri.nl/p/ProjectOverview?focusarea="
                 "http://purl.org/zonmw/generic/10006;"
                 "dataset=https://covid19initiatives.health-ri.nl/p/Project/27866022694497978",
            record=data, series_mapping=None)
        extras_dict = self._extras_to_dict(actual_dataset["extras"])

        assert actual_dataset["resources"] == []
        assert actual_dataset["title"] == "COVID-NL cohort MUMC+"
        assert actual_dataset["notes"] == "Clinical data of MUMC COVID-NL cohort"
        assert actual_dataset["tags"] == []
        assert actual_dataset["license_id"] == ""
        assert actual_dataset["has_version"] == [
            "https://repo.metadatacenter.org/template-instances/2836bf1c-76e9-44e7-a65e-80e9ca63025a"
        ]
        assert actual_dataset["contact"] == [
            {
                "email": "",
                "identifier": "https://orcid.org/0000-0002-4348-707X",
                "name": "N.K. De Vries",
                "uri": "",
                "url": "",
            }
        ]
        assert actual_dataset["creator"] == [
            {
                "email": "",
                "identifier": "",
                "name": "",
                "type": "",
                "uri": "https://orcid.org/0000-0002-0180-3636",
                "url": "",
            }
        ]
        assert actual_dataset["publisher"] == [
            {
                "email": "",
                "identifier": "",
                "name": "",
                "type": "",
                "uri": "https://opal.health-ri.nl/pub",
                "url": "",
            }
        ]
        assert actual_dataset["temporal_start"] == "2020-01-01"
        assert actual_dataset["temporal_end"] == "2025-12-31"
        assert actual_dataset["retention_period"] == []

        assert extras_dict["identifier"] == "27866022694497978"
        assert (
            extras_dict["uri"]
            == "https://covid19initiatives.health-ri.nl/p/Project/27866022694497978"
        )
        assert extras_dict["contact_name"] == "N.K. De Vries"
        assert (
            extras_dict["contact_identifier"]
            == "https://orcid.org/0000-0002-4348-707X"
        )
        assert (
            extras_dict["publisher_uri"] == "https://opal.health-ri.nl/pub"
        )
        assert extras_dict["creator_uri"] == "https://orcid.org/0000-0002-0180-3636"
        assert extras_dict["homepage"] == "http://localhost:5000"

    def test_fdp_record_converter_catalog_dict(self):
        fdp_record_to_package = FairDataPointRecordToPackageConverter(profile="fairdatapoint_dcat_ap")
        data = Graph().parse(Path(TEST_DATA_DIRECTORY, "fdp_catalog.ttl")).serialize()
        actual = fdp_record_to_package.record_to_package(
            guid="catalog=https://fair.healthinformationportal.eu/catalog/1c75c2c9-d2cc-44cb-aaa8-cf8c11515c8d",
            record=data, series_mapping=None)

        extras_dict = self._extras_to_dict(actual["extras"])

        assert actual["has_version"] == ["1.0"]
        assert actual["issued"] == "2023-10-06T10:12:55.614000+00:00"
        assert actual["modified"] == "2023-10-06T10:12:55.614000+00:00"
        assert actual["license_id"] == ""
        assert actual["publisher"] == [
            {
                "email": "",
                "identifier": "",
                "name": "Automatic",
                "type": "",
                "uri": "",
                "url": "",
            }
        ]
        assert actual["resources"] == []
        assert actual["tags"] == []
        assert actual["title"] == "Slovenia National Node"
        assert actual["retention_period"] == []

        assert (
            extras_dict["uri"]
            == "https://fair.healthinformationportal.eu/catalog/1c75c2c9-d2cc-44cb-aaa8-cf8c11515c8d"
        )
        assert (
            extras_dict["access_rights"]
            == "https://fair.healthinformationportal.eu/catalog/1c75c2c9-d2cc-44cb-aaa8-cf8c11515c8d#accessRights"
        )
        assert json.loads(extras_dict["conforms_to"]) == [
            "https://fair.healthinformationportal.eu/profile/a0949e72-4466-4d53-8900-9436d1049a4b"
        ]
        assert json.loads(extras_dict["language"]) == [
            "http://id.loc.gov/vocabulary/iso639-1/en"
        ]
        assert extras_dict["publisher_name"] == "Automatic"
        assert extras_dict["homepage"] == "http://localhost:5000"
