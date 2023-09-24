from rdflib.namespace import Namespace
from ckanext.dcat.profiles import EuropeanDCATAP2Profile
from ckan.plugins import toolkit
from ckan import model


def _convert_extras_to_declared_schema_fields(dataset_dict):
    '''
    Compares the extras dictionary with the declared schema.
    Updates the declared schema fields with the values that match from the extras.
    Remove the extras that are present on the declared schema.
    :param dataset_dict:
    :return: dataset_dict - Updated dataset_dict
    '''
    # Use the correct dataset type, Defaults to 'dataset'
    dataset_type = dataset_dict.get('type', 'dataset')
    # Gets the full Schema definition of the correct dataset type
    context = {'model': model, 'session': model.Session}
    data_dict = {'type': dataset_type}
    full_schema_dict = toolkit.get_action('scheming_dataset_schema_show')(context, data_dict)

    dataset_field_list = [x.get('field_name') for x in full_schema_dict.get('dataset_fields', [])]

    # Populate the declared schema fields, if they are present in the extras
    for extra_dict in dataset_dict.get('extras', []):
        if extra_dict.get('key') in dataset_field_list:
            dataset_dict[extra_dict.get('key')] = extra_dict.get('value')

    # Remove the extras that have been populated into the declared schema fields
    dataset_dict['extras'] = [d for d in dataset_dict['extras'] if d.get('key') not in dataset_field_list]

    return dataset_dict


class FAIRDataPointDCATAPProfile(EuropeanDCATAP2Profile):
    """
    An RDF profile for FAIR data points
    """

    def parse_dataset(self, dataset_dict, dataset_ref):
        super(FAIRDataPointDCATAPProfile, self).parse_dataset(dataset_dict, dataset_ref)

        dataset_dict = _convert_extras_to_declared_schema_fields(dataset_dict)

        # Example of adding a field
        dataset_dict['extras'].append({'key': 'hello',
                                       'value': "Hello from the FAIR data point profile. Use this function to do FAIR data point specific stuff during the import stage"})

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
