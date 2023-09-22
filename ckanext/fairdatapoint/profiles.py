from rdflib.namespace import Namespace
from ckanext.dcat.profiles import EuropeanDCATAP2Profile


class FAIRDataPointDCATAPProfile(EuropeanDCATAP2Profile):
    """
    An RDF profile for FAIR data points
    """

    def parse_dataset(self, dataset_dict, dataset_ref):
        super(FAIRDataPointDCATAPProfile, self).parse_dataset(dataset_dict, dataset_ref)

        # Example of adding a field
        dataset_dict['extras'].append({'key': 'hello', 'value': "Hello from the FAIR data point profile. Use this function to do FAIR data point specific stuff during the import stage"})

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
