from ckanext.fairdatapoint.label_lookups.label_lookup import ILabelLookup
from rdflib import URIRef


class BiontologyLabelLookup(ILabelLookup):

    pref_label_uri = URIRef('http://data.bioontology.org/metadata/skosprefLabel')

    def get_label(self, url, language):
        result = []

        g = self.get_graph(url, 'application/ld+json', 'json-ld')

        subject_uri = URIRef(url)
        for pref_label_literal in g.objects(subject=subject_uri, predicate=self.pref_label_uri):
            result.append(pref_label_literal.value)

        return ", ".join(result)
