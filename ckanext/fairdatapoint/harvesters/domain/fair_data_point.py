# SPDX-FileCopyrightText: 2023 Civity
# SPDX-FileContributor: 2024 Stichting Health-RI
#
# SPDX-License-Identifier: AGPL-3.0-only

import encodings
import logging
from typing import Union

import requests
from rdflib import Graph, URIRef
from rdflib.exceptions import ParserError
from requests.exceptions import ConnectionError, HTTPError, RequestException, Timeout

log = logging.getLogger(__name__)


class FairDataPoint:
    """Class to connect and get data from FDP"""

    def __init__(self, fdp_end_point: str):
        self.fdp_end_point = fdp_end_point

    def get_graph(self, path: Union[str, URIRef]) -> Graph:
        """
        Get graph from FDP at specified path. Not using function to load graph from endpoint directly since this
        function fails because of a certificate error. The library it uses probably has no certificates which would
        have to be added to a trust store. But this is inconvenient in case of a new harvester which refers to an
        endpoint whose certificate is not in the trust store yet.
        """
        graph = Graph()
        data = self._get_data(path)
        if data is None:
            log.warning(
                f"No data was received from FDP {self.fdp_end_point} request {path}"
            )
        else:
            try:
                graph.parse(data=data)
            except ParserError as e:
                log.error(f"Record {data} could not be parsed: {e}")
        return graph

    @staticmethod
    def _get_data(path: Union[str, URIRef]) -> Union[str, None]:
        headers = {"Accept": "text/turtle"}
        try:
            response = requests.request("GET", path, headers=headers)
            response.encoding = encodings.utf_8.getregentry().name
            response.raise_for_status()
            return response.text
        except (HTTPError, ConnectionError, Timeout, RequestException) as e:
            log.error(f"FDP query {path} was not successful: {e}")
