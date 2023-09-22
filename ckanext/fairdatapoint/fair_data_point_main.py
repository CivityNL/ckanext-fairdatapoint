# coding: utf8

from ckanext.fairdatapoint.harvesters.domain.fair_data_point_record_provider import FairDataPointRecordProvider


def main():
    # endpoints = ['https://fair.healthinformationportal.eu', 'https://health-ri.sandbox.semlab-leiden.nl']

    endpoints = ['https://health-ri.sandbox.semlab-leiden.nl']

    for endpoint in endpoints:
        record_provider = FairDataPointRecordProvider(endpoint)

        record_ids = record_provider.get_record_ids()
        for record_id in record_ids:
            data = record_provider.get_record_by_id(record_id)
            print(data)


if __name__ == "__main__":
    main()
