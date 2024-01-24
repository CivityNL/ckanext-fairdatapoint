# File original (C) Civity
# File modified by Stichting Health-RI in January 2024 to remove a debugging graph-print function
# All changes are © Stichting Health-RI and are licensed under the AGPLv3 license

import requests

from rdflib import Graph, URIRef
from rdflib.exceptions import ParserError
from typing import Union


class FairDataPoint:
    """Class to connect and get data from FDP"""

    def __init__(self, fdp_end_point: str):
        self.fdp_end_point = fdp_end_point

    def get_graph(self, path: Union[str, URIRef]) -> Union[Graph, None]:
        """
        Get graph from FDP at specified path. Not using function to load graph from endpoint directly since this
        function fails because of a certificate error. The library it uses probably has no certificates which would
        have to be added to a trust store. But this is inconvenient in case of a new harvester which refers to an
        endpoint whose certificate is not in the trust store yet.
        """
        try:
            g = Graph().parse(data=self._get_data(path))
        except ParserError as e:
            g = None

        return g

    @staticmethod
    def _get_data(path: Union[str, URIRef]) -> str:
        headers = {
            'Accept': 'text/turtle'
        }
        response = requests.request("GET", path, headers=headers)
        return response.text
