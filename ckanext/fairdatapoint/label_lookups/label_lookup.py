from abc import abstractmethod
from rdflib import Graph

import requests


class LabelLookupException(Exception):
    """
    Exception class for LabelLookup
    """
    pass


class ILabelLookup:

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

    @staticmethod
    def print_graph(g):
        for prefix, ns in g.namespaces():
            print(prefix, ns)

        for s, p, o in g:
            print(s, ' - ', p, ' - ', o)