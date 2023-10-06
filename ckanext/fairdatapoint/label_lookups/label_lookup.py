from abc import abstractmethod
from rdflib import Graph, URIRef

import requests


class LabelLookupException(Exception):
    """
    Exception class for LabelLookup
    """
    pass


class ILabelLookup:

    pref_label_predicate = URIRef('http://www.w3.org/2004/02/skos/core#prefLabel')

    def __init__(self):
        pass

    @abstractmethod
    def get_label(self, url, language):
        """Get a label from a URL for a language."""

        # TODO Python 3: use type and return annotations

        pass

    def get_graph(self, path, accept, rdf_format):
        g = Graph().parse(data=self._get_data(path, accept), format=rdf_format)
        return g

    @staticmethod
    def _get_data(path, accept):
        headers = {
            'Accept': accept
        }
        response = requests.request("GET", path, headers=headers)
        return response.text

    def extract_result(self, g, subject_uri, language):
        result = []

        subject_uri = URIRef(subject_uri.replace('https', 'http'))
        for pref_label_literal in g.objects(subject=subject_uri, predicate=self.pref_label_predicate):
            if language.lower() == pref_label_literal.language.lower():
                result.append(pref_label_literal.value)

        return ", ".join(result)

    @staticmethod
    def print_graph(g):
        for prefix, ns in g.namespaces():
            print(prefix, ns)

        for s, p, o in g:
            print(s, ' - ', p, ' - ', o)