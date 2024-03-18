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
from dateutil.tz import tzutc, tzoffset
from pathlib import Path
from rdflib import Graph, URIRef
from ckanext.fairdatapoint.profiles import validate_tags, convert_datetime_string
from ckanext.fairdatapoint.harvesters.domain.fair_data_point_record_to_package_converter import (
    FairDataPointRecordToPackageConverter)

TEST_DATA_DIRECTORY = Path(Path(__file__).parent.resolve(), "test_data")


@pytest.mark.parametrize("input_tags,expected_tags", [
    ([{"name": "CNS/Brain"}], [{"name": "CNS Brain"}]),
    ([{"name": "COVID-19"}, {"name": "3`-DNA"}], [{"name": "COVID-19"}, {"name": "3 -DNA"}]),
    ([{"name": "something-1.1"}, {"name": "breast cancer"}], [{"name": "something-1.1"}, {"name": "breast cancer"}]),
    ([], [])
])
def test_validate_tags(input_tags, expected_tags):
    actual_tags = validate_tags(input_tags)
    assert actual_tags == expected_tags


@pytest.mark.ckan_config("ckan.plugins", "scheming_datasets")
@pytest.mark.usefixtures("with_plugins")
def test_parse_dataset():
    """Dataset with keywords which should be modified"""
    fdp_record_to_package = FairDataPointRecordToPackageConverter(profile="fairdatapoint_dcat_ap")
    data = Graph().parse(Path(TEST_DATA_DIRECTORY, "dataset_cbioportal.ttl")).serialize()
    actual = fdp_record_to_package.record_to_package(
        guid="catalog=https://health-ri.sandbox.semlab-leiden.nl/catalog/5c85cb9f-be4a-406c-ab0a-287fa787caa0;"
             "dataset=https://health-ri.sandbox.semlab-leiden.nl/dataset/d9956191-1aff-4181-ac8b-16b829135ed5",
        record=data)
    expected = {
        'extras': [
            {'key': 'uri',
             'value': 'https://health-ri.sandbox.semlab-leiden.nl/dataset/d9956191-1aff-4181-ac8b-16b829135ed5'
             }
        ],
        'resources': [{'name': 'Clinical data for [PUBLIC] Low-Grade Gliomas (UCSF, Science 2014)',
                       'description': 'Clinical data for [PUBLIC] Low-Grade Gliomas (UCSF, Science 2014)',
                       'access_url': 'https://cbioportal.health-ri.nl/study/clinicalData?id=lgg_ucsf_2014',
                       'license': 'http://rdflicense.appspot.com/rdflicense/cc-by-nc-nd3.0',
                       'url': 'https://cbioportal.health-ri.nl/study/clinicalData?id=lgg_ucsf_2014',
                       'uri': 'https://health-ri.sandbox.semlab-leiden.nl/distribution/'
                              '931ed9c4-ad23-47ff-b121-2eb428e57423',
                       'distribution_ref': 'https://health-ri.sandbox.semlab-leiden.nl/distribution/'
                                           '931ed9c4-ad23-47ff-b121-2eb428e57423'},
                      {'name': 'Mutations',
                       'description': 'Mutation data from whole exome sequencing of 23 grade II glioma tumor/normal '
                                      'pairs. (MAF)',
                       'access_url': 'https://cbioportal.health-ri.nl/study/summary?id=lgg_ucsf_2014',
                       'license': 'http://rdflicense.appspot.com/rdflicense/cc-by-nc-nd3.0',
                       'url': 'https://cbioportal.health-ri.nl/study/summary?id=lgg_ucsf_2014',
                       'uri': 'https://health-ri.sandbox.semlab-leiden.nl/distribution/'
                              'ad00299f-6efb-42aa-823d-5ff2337f38f7',
                       'distribution_ref': 'https://health-ri.sandbox.semlab-leiden.nl/distribution/'
                                           'ad00299f-6efb-42aa-823d-5ff2337f38f7'}],
        'title': '[PUBLIC] Low-Grade Gliomas (UCSF, Science 2014)',
        'notes': 'Whole exome sequencing of 23 grade II glioma tumor/normal pairs.',
        'url': 'https://cbioportal.health-ri.nl/study/summary?id=lgg_ucsf_2014',
        'tags': [{'name': 'CNS Brain'}, {'name': 'Diffuse Glioma'}, {'name': 'Glioma'}], 'license_id': '',
        'issued': datetime(2019, 10, 30, 23, 0),
        'modified': datetime(2019, 10, 30, 23, 0),
        'identifier': 'lgg_ucsf_2014', 'language': ['http://id.loc.gov/vocabulary/iso639-1/en'],
        'conforms_to': ['https://health-ri.sandbox.semlab-leiden.nl/profile/2f08228e-1789-40f8-84cd-28e3288c3604'],
        'publisher_uri': 'https://www.health-ri.nl',
        'access_rights': 'https://health-ri.sandbox.semlab-leiden.nl/dataset/'
                         'd9956191-1aff-4181-ac8b-16b829135ed5#accessRights',
        'is_referenced_by': '["https://pubmed.ncbi.nlm.nih.gov/24336570"]'}
    assert actual == expected


@pytest.mark.parametrize("input_timestring,expected_output", [
    ("2023-10-06T10:12:55.614000+00:00",
     datetime(2023, 10, 6, 10, 12, 55, 614000, tzinfo=tzutc())),
    ("2024-02-15 11:16:37+03:00",
     datetime(2024, 2, 15, 11, 16, 37, tzinfo=tzoffset(None, 10800))),
    ("November 9, 1999", datetime(1999, 11, 9, 0, 0, 0)),
    ("2006-09", datetime(2006, 9, 18))])
def test_convert_datetime_string(input_timestring, expected_output):
    actual = convert_datetime_string(input_timestring)
    assert actual == expected_output
