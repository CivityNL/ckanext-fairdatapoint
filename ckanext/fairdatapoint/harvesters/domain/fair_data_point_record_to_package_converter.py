import logging

from ckanext.civity.harvesters.domain.record_to_package_converter import IRecordToPackageConverter

log = logging.getLogger(__name__)


class FairDataPointRecordToPackageConverter(IRecordToPackageConverter):

    def record_to_package(self, record):
        pass
