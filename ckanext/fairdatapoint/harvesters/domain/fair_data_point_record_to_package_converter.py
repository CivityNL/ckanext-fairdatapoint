import logging

from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF

from ckanext.civity.harvesters.domain.record_to_package_converter import \
    IRecordToPackageConverter, \
    RecordToPackageConverterException
from ckanext.fairdatapoint.harvesters.domain.fair_data_point import FairDataPoint

log = logging.getLogger(__name__)


class FairDataPointRecordToPackageConverter(IRecordToPackageConverter):

    def __init__(self, fdp_end_point, record_to_package_mapping, template_package_dict):
        IRecordToPackageConverter.__init__(self)
        self.fair_data_point = FairDataPoint(fdp_end_point)
        self.record_to_package_mapping = record_to_package_mapping
        self.template_package_dict = template_package_dict

    def record_to_package(self, record):
        if self.template_package_dict:
            return self._map_content_to_package(record)
        else:
            raise RecordToPackageConverterException(
                'Template package undefined for FAIR data point record to package converter'
            )

    def _map_content_to_package(self, content):
        log.info('Content to package for FAIR data point dataset')

        result = self.template_package_dict.copy()

        result['private'] = False

        g = Graph().parse(data=content)

        for (package_field_name, mapping) in self.record_to_package_mapping.items():
            source = mapping['source']

            result[package_field_name] = mapping['default']

            identifier_predicate = URIRef('http://purl.org/dc/terms/identifier')
            subject_id = None
            for identifier in g.objects(predicate=identifier_predicate):
                if '/' + source + '/' in identifier:
                    subject_id = identifier.replace(self.fair_data_point.fdp_end_point + '/' + source + '/', '')
                    break

            if subject_id is not None:
                subject_uri = URIRef(self.fair_data_point.fdp_end_point + '/' + source + '/' + subject_id)
                predicate_uri = URIRef(mapping['predicate'])
                for value in g.objects(subject=subject_uri, predicate=predicate_uri):
                    result[package_field_name] = value
            else:
                raise RecordToPackageConverterException('Subject identifier not found')

        return result
