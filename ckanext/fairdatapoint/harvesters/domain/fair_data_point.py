import requests

from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF



class FairDataPoint:

    def __init__(self, fdp_end_point):
        self.fdp_end_point = fdp_end_point

    def get_graph(self, path):
        """
        Get graph from FDP at specified path. Not using function to load graph from endpoint directly since this
        function fails because of a certificate error. The library it uses probable has no certificates which would
        have to be added to a trust store. But this is inconvenient in case of a new harvester which refers to an
        endpoint whose certificate is not in the trust store yet.
        """
        g = Graph().parse(data=self._get_data(path))
        return g

    def _get_data(self, path):
        response = requests.request("GET", self._get_uri(path))
        return response.text

    def _get_uri(self, path):
        return self.fdp_end_point + path

    @staticmethod
    def print_graph(g):
        for prefix, ns in g.namespaces():
            print(prefix, ns)

        for s, p, o in g:
            print(s, ' - ', p, ' - ', o)
