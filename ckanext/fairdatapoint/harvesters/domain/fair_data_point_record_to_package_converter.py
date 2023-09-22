import logging

from ckanext.civity.harvesters.domain.record_to_package_converter import \
    IRecordToPackageConverter, \
    RecordToPackageConverterException
from ckanext.fairdatapoint.harvesters.domain.identifier import Identifier
from ckanext.dcat.processors import RDFParser, RDFParserException
from ckanext.fairdatapoint.processors import FairDataPointRDFParser

log = logging.getLogger(__name__)


class FairDataPointRecordToPackageConverter(IRecordToPackageConverter):

    def __init__(self, profile):
        IRecordToPackageConverter.__init__(self)
        self.profile = profile

    def record_to_package(self, guid, record):
        parser = FairDataPointRDFParser(profiles=[self.profile])

        try:
            parser.parse(record, _format='ttl')

            identifier = Identifier(guid)
            if identifier.get_id_type() == 'catalog':
                for catalog in parser.catalogs():
                    return catalog
            else:
                for dataset in parser.datasets():
                    return dataset
        except RDFParserException as e:
            raise RecordToPackageConverterException('Error parsing the RDF content [{0}]: {1}'.format(record, e))
