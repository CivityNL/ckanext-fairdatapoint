import logging

from ckanext.civity.harvesters.domain.record_provider import IRecordProvider, RecordProviderException
from ckanext.fairdatapoint.harvesters.domain.identifier import Identifier

from ckanext.fairdatapoint.harvesters.domain.fair_data_point import FairDataPoint

from rdflib import Namespace, URIRef, Literal
from rdflib.namespace import RDF

DC_TERMS_DESCRIPTION = 'http://purl.org/dc/terms/description'
DC_TERMS_FORMAT = 'http://purl.org/dc/terms/format'
DC_TERMS_LICENSE = 'http://purl.org/dc/terms/license'
DC_TERMS_TITLE = 'http://purl.org/dc/terms/title'
DCAT_ACCESS_URL = 'http://www.w3.org/ns/dcat#accessURL'

log = logging.getLogger(__name__)


class FairDataPointRecordProviderException(RecordProviderException):
    pass


class FairDataPointRecordProvider(IRecordProvider):
    dcat = Namespace('http://www.w3.org/ns/dcat#')
    ldp = Namespace('http://www.w3.org/ns/ldp#')

    def __init__(self, fdp_end_point):
        IRecordProvider.__init__(self)
        self.fair_data_point = FairDataPoint(fdp_end_point)

    def get_record_ids(self):
        """
        Return all the FDP records which should end up as packages in CKAN to populate the "guids_in_harvest" list
        https://rdflib.readthedocs.io/en/stable/intro_to_parsing.html
        """
        log.debug('FAIR Data Point get_records from {}'.format(self.fair_data_point.fdp_end_point))

        result = dict()

        catalogs_graph = self.fair_data_point.get_graph("/page/catalog")

        for catalog_subject in catalogs_graph.subjects(RDF.type, self.dcat.Catalog):
            identifier = Identifier('')

            catalog_id = catalog_subject.replace(self.fair_data_point.fdp_end_point + '/catalog/', '')

            identifier.add('catalog', catalog_id)

            result[identifier.guid] = catalog_subject

            catalog_graph = self.fair_data_point.get_graph('/catalog/' + catalog_id)
            dataset_predicate = URIRef('http://www.w3.org/ns/dcat#dataset')
            for dataset_uri in catalog_graph.objects(predicate=dataset_predicate):
                dataset_id = dataset_uri.replace(self.fair_data_point.fdp_end_point + '/dataset/', '')

                identifier.add('dataset', dataset_id)

                result[identifier.guid] = dataset_uri

        return result.keys()

    def get_record_by_id(self, guid):
        """
        Get additional information for FDP record.
        """
        log.debug('FAIR data point get_record_by_id from {} for {}'.format(self.fair_data_point.fdp_end_point, guid))

        identifier = Identifier(guid)

        g = self.fair_data_point.get_graph('/' + identifier.get_id_type() + '/' + identifier.get_id_value())

        subject_uri = URIRef(
            self.fair_data_point.fdp_end_point + '/' +
            identifier.get_id_type() + '/' +
            identifier.get_id_value()
        )

        distribution_predicate_uri = URIRef('http://www.w3.org/ns/dcat#distribution')

        # Add information from distribution to graph
        # Lookup resource name (dcterms:title) and resource description (dcterms:description) for Distribution/resource
        for distribution_uri in g.objects(subject=subject_uri, predicate=distribution_predicate_uri):
            distribution_id = distribution_uri.replace(self.fair_data_point.fdp_end_point + '/distribution/', '')

            distribution_g = self.fair_data_point.get_graph('/distribution/' + distribution_id)

            distribution = URIRef(distribution_uri)

            for predicate in [
                DC_TERMS_DESCRIPTION,
                DC_TERMS_FORMAT,
                DC_TERMS_LICENSE,
                DC_TERMS_TITLE,
                DCAT_ACCESS_URL
            ]:
                for literal in self.get_values(distribution_g, distribution_uri, predicate):
                    g.add((distribution, URIRef(predicate), literal))

        result = g.serialize(format='ttl')

        return result

    @staticmethod
    def get_values(graph, subject, predicate):

        subject_uri = URIRef(subject)
        predicate_uri = URIRef(predicate)

        for value in graph.objects(subject=subject_uri, predicate=predicate_uri):
            yield value
