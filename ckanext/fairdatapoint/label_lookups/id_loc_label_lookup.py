from ckanext.fairdatapoint.label_lookups.label_lookup import ILabelLookup
from rdflib import URIRef


class IdLocLabelLookup(ILabelLookup):

    def get_label(self, url, language):
        g = self.get_graph(url + '.json', 'application/ld+json', 'json-ld')
        return self.extract_result(g, url, language)
