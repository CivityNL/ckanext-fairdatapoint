from ckanext.fairdatapoint.label_lookups.label_lookup import ILabelLookup
from rdflib import URIRef


class WikidataLabelLookup(ILabelLookup):

    pref_label_predicate = URIRef('http://www.w3.org/2004/02/skos/core#prefLabel')

    def get_label(self, url, language):
        g = self.get_graph(url.replace('/wiki/', '/wiki/Special:EntityData/') + '.ttl', 'text/turtle', 'turtle')
        return self.extract_result(g, url.replace('/wiki/', '/entity/'), language)
