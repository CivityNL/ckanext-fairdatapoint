import logging
import json

from rdflib import Graph, URIRef

from ckanext.civity.harvesters.domain.record_to_package_converter import \
    IRecordToPackageConverter, \
    RecordToPackageConverterException
from ckanext.fairdatapoint.harvesters.domain.fair_data_point import FairDataPoint
from ckanext.fairdatapoint.harvesters.domain.identifier import Identifier

log = logging.getLogger(__name__)


class FairDataPointRecordToPackageConverter(IRecordToPackageConverter):

    def __init__(self, fdp_end_point, record_to_package_mapping, template_package_dict):
        IRecordToPackageConverter.__init__(self)
        self.fair_data_point = FairDataPoint(fdp_end_point)
        self.record_to_package_mapping = record_to_package_mapping
        self.template_package_dict = template_package_dict

    def record_to_package(self, identifier, record):
        if self.template_package_dict:
            return self._map_content_to_package(identifier, record)
        else:
            raise RecordToPackageConverterException(
                'Template package undefined for FAIR data point record to package converter'
            )

    def _map_content_to_package(self, guid, content):
        log.info('Content to package for FAIR data point dataset')

        identifier = Identifier(guid)

        result = self.template_package_dict.copy()

        result['id'] = identifier.get_id_value()

        result['type'] = 'dataset'  # identifier.get_id_type()

        result['url'] = self.fair_data_point.fdp_end_point + '/' + identifier.get_id_type() + '/' + identifier.get_id_value()

        result['private'] = False

        g = Graph().parse(data=content)

        subject_uri = URIRef(
            self.fair_data_point.fdp_end_point + '/' +
            identifier.get_id_type() + '/' +
            identifier.get_id_value()
        )

        for (package_field_name, mapping) in self.record_to_package_mapping.items():
            if 'predicate' in mapping.keys() and len(mapping['predicate']) > 0:
                predicate_uri = URIRef(mapping['predicate'])

                values = []

                for value in g.objects(subject=subject_uri, predicate=predicate_uri):
                    values.append(value)

                result[package_field_name] = ', '.join(values)
            else:
                result[package_field_name] = mapping['default']

        return result
