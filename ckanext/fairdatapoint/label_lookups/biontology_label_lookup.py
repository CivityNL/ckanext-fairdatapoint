from ckanext.fairdatapoint.label_lookups.label_lookup import ILabelLookup
from rdflib import URIRef


class BiontologyLabelLookup(ILabelLookup):

    alternative_pref_label_predicate = URIRef('http://data.bioontology.org/metadata/skosprefLabel')

    def get_label(self, url, language):
        g = self.get_graph(url, 'application/ld+json', 'json-ld')
        return self.extract_result_without_language(g, url)

    def get_pref_label_predicate(self):
        return self.alternative_pref_label_predicate
