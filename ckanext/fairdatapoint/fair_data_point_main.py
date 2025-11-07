# SPDX-FileCopyrightText: 2023 Civity
# SPDX-FileContributor: 2024 Stichting Health-RI
#
# SPDX-License-Identifier: AGPL-3.0-only

# coding: utf8

from ckanext.fairdatapoint.harvesters.domain.fair_data_point_record_provider import (
    FairDataPointRecordProvider,
)


def main():
    endpoints = [
        "https://fair.healthinformationportal.eu",
        "https://health-ri.sandbox.semlab-leiden.nl/",
        "https://portal-gdi-nl.molgeniscloud.org/api/fdp/",
    ]

    for endpoint in endpoints:
        print("!@#$%^&*()_+", endpoint, "+_)(*&^%$#@!")
        record_provider = FairDataPointRecordProvider(endpoint)

        record_ids = record_provider.get_record_ids()
        for record_id in record_ids:
            print(record_id)
            if "dataset=" in record_id:
                data = record_provider.get_record_by_id(record_id)
                print(data)
                break


if __name__ == "__main__":
    main()
