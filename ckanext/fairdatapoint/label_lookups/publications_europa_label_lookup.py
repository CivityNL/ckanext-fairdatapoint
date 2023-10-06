from ckanext.fairdatapoint.label_lookups.label_lookup import ILabelLookup
from rdflib import URIRef


class PublicationsEuropaLabelLookup(ILabelLookup):

    pref_label_predicate = URIRef('http://www.w3.org/2004/02/skos/core#prefLabel')

    def get_label(self, url, language):
        g = self.get_graph(url, 'application/rdf+xml', 'xml')
        return self.extract_result(g, url, language)
