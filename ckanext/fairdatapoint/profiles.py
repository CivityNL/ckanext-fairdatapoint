# File original (C) Civity
# File modified by Stichting Health-RI in January 2024 to rename the dataset_fields variable and
#  check for multiple-text fields in the schema
# All changes are © Stichting Health-RI and are licensed under the AGPLv3 license

from datetime import datetime
import re
import json
import logging

from ckanext.dcat.profiles import EuropeanDCATAP2Profile
from ckan.plugins import toolkit
from ckan import model
import dateutil.parser as dateparser
from dateutil.parser import ParserError
from typing import Dict, List
from rdflib import URIRef

log = logging.getLogger(__name__)


def _convert_extras_to_declared_schema_fields(dataset_dict: Dict) -> Dict:
    """
    Compares the extras dictionary with the declared schema.
    Updates the declared schema fields with the values that match from the extras.
    Remove the extras that are present on the declared schema.
    :param dataset_dict:
    :return: dataset_dict - Updated dataset_dict
    """
    # Use the correct dataset type, Defaults to 'dataset'
    dataset_type = dataset_dict.get('type', 'dataset')
    # Gets the full Schema definition of the correct dataset type
    context = {'model': model, 'session': model.Session}
    data_dict = {'type': dataset_type}
    full_schema_dict = toolkit.get_action('scheming_dataset_schema_show')(context, data_dict)

    dataset_fields = {x.get('field_name'): x.get('preset') for x in full_schema_dict.get('dataset_fields', [])}

    # Populate the declared schema fields, if they are present in the extras
    for extra_dict in dataset_dict.get('extras', []):
        field_key = extra_dict.get('key')
        field_value = extra_dict.get('value')
        if field_key in dataset_fields:
            preset = dataset_fields[field_key]
            if preset == 'multiple_text' and field_value:
                dataset_dict[field_key] = json.loads(field_value)
            elif preset == 'date' and field_value:
                dataset_dict[field_key] = convert_datetime_string(field_value)
            else:
                dataset_dict[field_key] = field_value

    # Remove the extras that have been populated into the declared schema fields
    dataset_dict['extras'] = [d for d in dataset_dict['extras'] if d.get('key') not in dataset_fields]

    return dataset_dict


def validate_tags(values_list: List[Dict]) -> List:
    """
    Validates tags strings to contain allowed characters, replaces others with spaces
    """
    illegal_pattern = re.compile('[^A-Za-z0-9\- _\.]')
    tags = []
    for item in values_list:
        tag_value = item['name']
        find_illegal = re.search(illegal_pattern, tag_value)
        if find_illegal:
            log.warning(f'Tag {tag_value} contains values other than alphanumeric characters, spaces, hyphens, '
                        f'underscores or dots, they will be replaces with spaces')
            tag = {'name': re.sub(illegal_pattern, ' ', tag_value)}
            tags.append(tag)
        else:
            tags.append(item)
    return tags


def convert_datetime_string(date_value: str) -> datetime:
    """
    Converts datestrings (e.g. '2023-10-06T10:12:55.614000+00:00') to datetime class instance
    """
    try:
        date_value = dateparser.parse(date_value)
    except ParserError:
        log.error('A date field string value can not be parsed to a date')
    return date_value


class FAIRDataPointDCATAPProfile(EuropeanDCATAP2Profile):
    """
    An RDF profile for FAIR data points
    """

    def parse_dataset(self, dataset_dict: Dict, dataset_ref: URIRef) -> Dict:
        super(FAIRDataPointDCATAPProfile, self).parse_dataset(dataset_dict, dataset_ref)

        dataset_dict = _convert_extras_to_declared_schema_fields(dataset_dict)

        dataset_dict['tags'] = validate_tags(dataset_dict['tags'])

        # Example of adding a field
        # dataset_dict['extras'].append({'key': 'hello',
        #                                'value': 'Hello from the FAIR data point profile. Use this function to do '
        #                                         'FAIR data point specific stuff during the import stage'})

        return dataset_dict

    # def graph_from_dataset(self, dataset_dict, dataset_ref):
    #
    #     g = self.g
    #
    #     spatial_text = self._get_dataset_value(dataset_dict, 'hello')
    #
    #     if spatial_uri:
    #         spatial_ref = URIRef(spatial_uri)
    #     else:
    #         spatial_ref = BNode()
    #
    #     if spatial_text:
    #         g.add((dataset_ref, DCT.spatial, spatial_ref))
    #         g.add((spatial_ref, RDF.type, DCT.Location))
    #         g.add((spatial_ref, RDFS.label, Literal(spatial_text)))
