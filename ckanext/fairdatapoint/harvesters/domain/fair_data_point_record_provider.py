# File original (C) Civity
# File modified by Stichting Health-RI in January 2024 to remove custom exception and dependency on
#  Civity-specific record provider
# All changes are © Stichting Health-RI and are licensed under the AGPLv3 license


import logging

import requests

from ckanext.fairdatapoint.harvesters.domain.identifier import Identifier
from ckanext.fairdatapoint.harvesters.domain.fair_data_point import FairDataPoint

from rdflib import Namespace, URIRef, Literal, DCAT, DCTERMS, Graph, RDF
from rdflib.term import Node
from typing import Dict, Iterable, Union


LDP = Namespace('http://www.w3.org/ns/ldp#')
VCARD = Namespace('http://www.w3.org/2006/vcard/ns#')

log = logging.getLogger(__name__)


class FairDataPointRecordProvider:

    def __init__(self, fdp_end_point: str):
        self.fair_data_point = FairDataPoint(fdp_end_point)

    def get_record_ids(self) -> Dict.keys:
        """
        Returns all the FDP records which should end up as packages in CKAN to populate the "guids_in_harvest" list
        https://rdflib.readthedocs.io/en/stable/intro_to_parsing.html
        """
        log.debug('FAIR Data Point get_records from {}'.format(self.fair_data_point.fdp_end_point))

        result = dict()

        fdp_graph = self.fair_data_point.get_graph(self.fair_data_point.fdp_end_point)

        contains_predicate = LDP.contains
        for contains_object in fdp_graph.objects(predicate=contains_predicate):
            result.update(self._process_catalog(str(contains_object)))

        return result.keys()

    def _process_catalog(self, path: Union[str, URIRef]) -> Dict:
        result = dict()

        catalogs_graph = self.fair_data_point.get_graph(path)

        if catalogs_graph is not None:
            for catalog_subject in catalogs_graph.subjects(RDF.type, DCAT.Catalog):
                identifier = Identifier('')

                identifier.add('catalog', str(catalog_subject))

                result[identifier.guid] = catalog_subject

                catalog_graph = self.fair_data_point.get_graph(catalog_subject)

                for dataset_subject in catalog_graph.objects(predicate=DCAT.dataset):
                    identifier = Identifier('')

                    identifier.add('catalog', str(catalog_subject))

                    identifier.add('dataset', str(dataset_subject))

                    result[identifier.guid] = dataset_subject

        return result

    def get_record_by_id(self, guid: str) -> str:
        """
        Get additional information for FDP record.
        """
        log.debug(
            'FAIR data point get_record_by_id from {} for {}'.format(self.fair_data_point.fdp_end_point, guid))

        identifier = Identifier(guid)

        subject_url = identifier.get_id_value()

        g = self.fair_data_point.get_graph(subject_url)

        subject_uri = URIRef(subject_url)

        # Add information from distribution to graph
        for distribution_uri in g.objects(subject=subject_uri, predicate=DCAT.distribution):
            distribution_g = self.fair_data_point.get_graph(distribution_uri)

            for predicate in [
                DCTERMS.description,
                DCTERMS.format,
                DCTERMS.license,
                DCTERMS.title,
                DCAT.accessURL
            ]:
                for distr_attribute_value in self.get_values(distribution_g, distribution_uri, predicate):
                    g.add((distribution_uri, predicate, distr_attribute_value))

        # Look-up contact information
        for contact_point_uri in self.get_values(g, subject_uri, DCAT.contactPoint):
            if 'orcid' in contact_point_uri:
                orcid_response = requests.get(str(contact_point_uri) + '/public-record.json')
                json_orcid_response = orcid_response.json()
                name = json_orcid_response['displayName']
                name_literal = Literal(name)
                g.add((subject_uri, VCARD.fn, name_literal))
                # TODO add original Orcid URL in a field

        result = g.serialize(format='ttl')

        return result

    @staticmethod
    def get_values(graph: Graph,
                   subject: Union[str, URIRef, Node],
                   predicate: Union[str, URIRef, Node]) -> Iterable[Node]:
        subject_uri = URIRef(subject)
        predicate_uri = URIRef(predicate)

        for value in graph.objects(subject=subject_uri, predicate=predicate_uri):
            yield value
