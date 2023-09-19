import logging
import urllib
import requests

from ckanext.civity.harvester.domain.record_provider import IRecordProvider

from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF

log = logging.getLogger(__name__)


class FairDataPointRecordProvider(IRecordProvider):

    dcat = Namespace('http://www.w3.org/ns/dcat#')
    ldp = Namespace('http://www.w3.org/ns/ldp#')

    def __init__(
            self,
            fdp_end_point
    ):
        IRecordProvider.__init__(self)
        self.fdp_end_point = fdp_end_point

    def get_record_ids(self):
        """
        Return all the FDP records which should end up as packages in CKAN to populate the "guids_in_harvest" list
        https://rdflib.readthedocs.io/en/stable/intro_to_parsing.html
        """
        log.debug('FAIR Data Point get_records from {}'.format(self.fdp_end_point))

        result = dict()

        catalogs_graph = self._get_graph("/page/catalog")

        for catalog_subject in catalogs_graph.subjects(RDF.type, self.dcat.Catalog):
            catalog_graph = self._get_graph(catalog_subject.replace(self.fdp_end_point, ''))

            dataset_predicate = URIRef("http://www.w3.org/ns/dcat#dataset")

            for dataset_uri in catalog_graph.objects(predicate=dataset_predicate):
                result[dataset_uri.replace(self.fdp_end_point + '/dataset/', '')] = dataset_uri

        return result.keys()

    def get_record_by_id(self, guid):
        """
        Get additional information for FDP record.
        """
        log.debug('Gisweb get_record_by_id for {}'.format(guid))

        result = self._get_theme(guid)

        result.theme_metadata = self._get_theme_metadata(guid)

        result.wms_layers = self._get_wms_layers(result.code)

        result.parent_theme_group = self._get_parent_theme_group(self._get_themes().get(guid))

        return result

    def _get_graph(self, path):
        """
        Get graph from FDP at specified path. Not using function to load graph from endpoint directly since this
        function fails because of a certificate error. The library it uses probable has no certificates which would
        have to be added to a trust store. But this is inconvenient in case of a new harvester which refers to an
        endpoint whose certificate is not in the trust store yet.
        """
        url = self.fdp_end_point + path

        response = requests.request("GET", url)

        g = Graph().parse(data=response.text)

        return g

    def _print_graph(self, g):
        for prefix, ns in g.namespaces():
            print(prefix, ns)

        for s, p, o in g:
            print(s, ' - ', p, ' - ', o)

