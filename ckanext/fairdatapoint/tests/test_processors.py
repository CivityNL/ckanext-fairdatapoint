"""
    CKAN Fair Data Point extension Test Suite
    Copyright (C) 2024, Stichting Health-RI

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import pytest
from datetime import datetime
from dateutil.tz import tzutc
from pathlib import Path
from unittest.mock import patch
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
            record=data)
        assert parser_catalogs.called

    def test_fdp_record_converter_dataset_dict(self):
        fdp_record_to_package = FairDataPointRecordToPackageConverter(profile="fairdatapoint_dcat_ap")
        data = Graph().parse(Path(TEST_DATA_DIRECTORY, "Project_27866022694497978_out.ttl")).serialize()
        actual_dataset = fdp_record_to_package.record_to_package(
            guid="catalog=https://covid19initiatives.health-ri.nl/p/ProjectOverview?focusarea="
                 "http://purl.org/zonmw/generic/10006;"
                 "dataset=https://covid19initiatives.health-ri.nl/p/Project/27866022694497978",
            record=data)
        expected_dataset = {"extras":
            [
                {"key": "uri", "value": "https://covid19initiatives.health-ri.nl/p/Project/27866022694497978"}
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
            "temporal_start": datetime(2020, 1, 1, 0, 0),
            "temporal_end": datetime(2025, 12, 31, 0, 0)}
        assert actual_dataset == expected_dataset

    def test_fdp_record_converter_catalog_dict(self):
        fdp_record_to_package = FairDataPointRecordToPackageConverter(profile="fairdatapoint_dcat_ap")
        data = Graph().parse(Path(TEST_DATA_DIRECTORY, "fdp_catalog.ttl")).serialize()
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
                       ],
            "has_version": ["1.0"],
            "issued": datetime(2023, 10, 6, 10, 12, 55, 614000, tzinfo=tzutc()),
            "language": ["http://id.loc.gov/vocabulary/iso639-1/en"],
            "license_id": "",
            "modified": datetime(2023, 10, 6, 10, 12, 55, 614000, tzinfo=tzutc()),
            "publisher_name": "Automatic",
            "resources": [],
            "tags": [],
            "title": "Slovenia National Node"
        }
        assert actual == expected
