# File original (C) Civity
# File modified by Stichting Health-RI in January 2024 to rename the dataset_fields variable and
#  check for multiple-text fields in the schema
# All changes are © Stichting Health-RI and are licensed under the AGPLv3 license

from ckanext.dcat.profiles import EuropeanDCATAP2Profile
from ckan.plugins import toolkit
from ckan import model
import json
from typing import Dict
from rdflib import URIRef


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
        if field_key in dataset_fields:
            preset = dataset_fields[field_key]
            if preset == "multiple_text" and extra_dict.get('value'):
                dataset_dict[field_key] = json.loads(extra_dict.get('value'))
            else:
                dataset_dict[field_key] = extra_dict.get('value')

    # Remove the extras that have been populated into the declared schema fields
    dataset_dict['extras'] = [d for d in dataset_dict['extras'] if d.get('key') not in dataset_fields]

    return dataset_dict


class FAIRDataPointDCATAPProfile(EuropeanDCATAP2Profile):
    """
    An RDF profile for FAIR data points
    """

    def parse_dataset(self, dataset_dict: Dict, dataset_ref: URIRef) -> Dict:
        super(FAIRDataPointDCATAPProfile, self).parse_dataset(dataset_dict, dataset_ref)

        dataset_dict = _convert_extras_to_declared_schema_fields(dataset_dict)

        # Example of adding a field
        dataset_dict['extras'].append({'key': 'hello',
                                       'value': "Hello from the FAIR data point profile. Use this function to do "
                                                "FAIR data point specific stuff during the import stage"})

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
