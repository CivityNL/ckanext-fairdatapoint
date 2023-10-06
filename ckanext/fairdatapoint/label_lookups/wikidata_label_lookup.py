from ckanext.fairdatapoint.label_lookups.label_lookup import ILabelLookup
from rdflib import URIRef


class WikidataLabelLookup(ILabelLookup):

    pref_label_predicate = URIRef('http://www.w3.org/2004/02/skos/core#prefLabel')

    def get_label(self, url, language):
        result = []

        ttl_url = url.replace('/wiki/', '/wiki/Special:EntityData/') + '.ttl'

        g = self.get_graph(ttl_url, 'text/turtle', 'turtle')

        entity_url = url.replace('/wiki/', '/entity/').replace('https', 'http')

        subject_uri = URIRef(entity_url)
        for pref_label_literal in g.objects(subject=subject_uri, predicate=self.pref_label_predicate):
            if language.lower() == pref_label_literal.language:
                result.append(pref_label_literal.value)

        # self.print_graph(g)

        return ", ".join(result)
