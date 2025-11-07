# SPDX-FileCopyrightText: 2023 Civity
# SPDX-FileContributor: 2024 Stichting Health-RI
#
# SPDX-License-Identifier: AGPL-3.0-only

from rdflib import DCAT, RDF, URIRef


class FdpRecord:
    def __init__(self, url, graph):
        self.url = url
        self._children = set()
        self._graph = graph

    def children(self):
        return self._children

    def add_children(self, child_url):
        self._children.add(child_url)

    def is_catalog(self):
        return (URIRef(self.url), RDF.type, DCAT.Catalog) in self._graph

    def is_dataset(self):
        return (URIRef(self.url), RDF.type, DCAT.Dataset) in self._graph

    def is_dataseries(self):
        return (URIRef(self.url), RDF.type, DCAT.DatasetSeries) in self._graph
    