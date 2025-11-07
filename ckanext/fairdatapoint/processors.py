# SPDX-FileCopyrightText: 2023 Civity
# SPDX-FileContributor: 2024 Stichting Health-RI
#
# SPDX-License-Identifier: AGPL-3.0-only

from typing import Dict, Iterable

from rdflib import DCAT, RDF
from rdflib.term import Node

from ckanext.dcat.processors import RDFParser


class FairDataPointRDFParser(RDFParser):

    def _catalogs(self) -> Iterable[Node]:
        """
        Generator that returns all DCAT catalogs on the graph

        Yields rdflib.term.URIRef objects that can be used on graph lookups
        and queries
        """
        for catalog in self.g.subjects(RDF.type, DCAT.Catalog):
            yield catalog

    def catalogs(self) -> Iterable[Dict]:
        """
        Generator that returns CKAN catalogs parsed from the RDF graph

        Each catalog is passed to all the loaded profiles before being
        yielded, so it can be further modified by each one of them.

        Returns a catalog dict that can be passed to eg `package_create`
        or `package_update`
        """
        for catalog_ref in self._catalogs():
            catalog_dict = {}
            for profile_class in self._profiles:
                profile = profile_class(
                    graph=self.g, compatibility_mode=self.compatibility_mode
                )
                profile.parse_dataset(catalog_dict, catalog_ref)

            yield catalog_dict
