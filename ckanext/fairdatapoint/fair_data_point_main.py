# coding: utf8
from ckanext.fairdatapoint.harvesters.domain.fair_data_point_record_provider import FairDataPointRecordProvider


def main():
    f = FairDataPointRecordProvider('https://health-ri.sandbox.semlab-leiden.nl')
    dataset_ids = f.get_record_ids()
    for dataset_id in dataset_ids:
        print('Dataset ID from FAIR data point:', dataset_id)


if __name__ == "__main__":
    main()
