# coding: utf8
import json

from ckanext.fairdatapoint.harvesters.domain.fair_data_point_record_provider import FairDataPointRecordProvider
from ckanext.fairdatapoint.harvesters.domain.fair_data_point_record_to_package_converter import \
    FairDataPointRecordToPackageConverter


def main():
    # endpoints = ['https://fair.healthinformationportal.eu', 'https://health-ri.sandbox.semlab-leiden.nl']

    endpoints = ['https://health-ri.sandbox.semlab-leiden.nl']

    for endpoint in endpoints:
        record_provider = FairDataPointRecordProvider(endpoint)
        record_ids = record_provider.get_record_ids()
        for record_id in record_ids:
            if 'catalog' in record_id and 'dataset' in record_id and 'distribution' not in record_id:
                data = record_provider.get_record_by_id(record_id)
                record_to_package_converter = FairDataPointRecordToPackageConverter(
                    endpoint,
                    json.load(open('dataset.json')),
                    json.load(open('template.json'))
                )
                print(json.dumps(record_to_package_converter.record_to_package(data)))


if __name__ == "__main__":
    main()
