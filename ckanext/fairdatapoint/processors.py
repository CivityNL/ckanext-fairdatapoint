from rdflib import RDF, Namespace

from ckanext.dcat.processors import RDFParser

DCAT = Namespace("http://www.w3.org/ns/dcat#")


class FairDataPointRDFParser(RDFParser):

    def _catalogs(self):
        """
        Generator that returns all DCAT catalogs on the graph

        Yields rdflib.term.URIRef objects that can be used on graph lookups
        and queries
        """
        for catalog in self.g.subjects(RDF.type, DCAT.Catalog):
            yield catalog

    def catalogs(self):
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
                profile = profile_class(self.g, self.compatibility_mode)
                profile.parse_dataset(catalog_dict, catalog_ref)

            yield catalog_dict
