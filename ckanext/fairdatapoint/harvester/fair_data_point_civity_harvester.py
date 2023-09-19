import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

import logging

from ckanext.civity.harvester.civity_harvester import CivityHarvester
from ckanext.fairdatapoint.harvester.domain.fair_data_point_record_provider import FairDataPointRecordProvider
from ckanext.fairdatapoint.harvester.domain.fair_data_point_record_to_package_converter import FairDataPointRecordToPackageConverter
# from ckanext.gisweb.lib.gisweb_record_to_package_converter import GiswebRecordToPackageConverter


class FairDataPointCivityHarvester(CivityHarvester):

    def __init__(self):
        self.record_to_package_converter = None
        self.record_provider = None

    def setup_record_provider(self, harvest_url, harvest_config_dict):
        self.record_provider = FairDataPointRecordProvider('https://example.com')

    def setup_record_to_package_converter(self, harvest_url, harvest_config_dict):
        self.record_to_package_converter = FairDataPointRecordToPackageConverter()

    def info(self):
        return {
            'name': 'fair_data_point_harvester',
            'title': 'FAIR data point harvester',
            'description': 'Harvester for end points implementing the FAIR data point protocol'
        }
