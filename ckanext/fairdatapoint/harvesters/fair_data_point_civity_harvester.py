from ckanext.civity.harvesters.civity_harvester import CivityHarvester, CivityHarvesterException
from ckanext.fairdatapoint.harvesters.domain.fair_data_point_record_provider import FairDataPointRecordProvider
from ckanext.fairdatapoint.harvesters.domain.fair_data_point_record_to_package_converter import \
    FairDataPointRecordToPackageConverter

MAPPING = 'mapping'


class FairDataPointCivityHarvester(CivityHarvester):

    def setup_record_provider(self, harvest_url, harvest_config_dict):
        self.record_provider = FairDataPointRecordProvider(harvest_url)

    def setup_record_to_package_converter(self, harvest_url, harvest_config_dict):
        if MAPPING in harvest_config_dict.keys():
            self.record_to_package_converter = FairDataPointRecordToPackageConverter(
                harvest_url,
                harvest_config_dict.get(MAPPING),
                self._get_template_package_dict(harvest_config_dict)
            )
        else:
            raise CivityHarvesterException('[{0}] node found in harvester config JSON'.format(MAPPING))

    def info(self):
        return {
            'name': 'fair_data_point_harvester',
            'title': 'FAIR data point harvester',
            'description': 'Harvester for end points implementing the FAIR data point protocol'
        }
