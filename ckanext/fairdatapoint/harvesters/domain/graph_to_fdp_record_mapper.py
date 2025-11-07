# SPDX-FileCopyrightText: 2023 Civity
# SPDX-FileContributor: 2024 Stichting Health-RI
#
# SPDX-License-Identifier: AGPL-3.0-only

from ckanext.fairdatapoint.harvesters.domain.fdp_record import FdpRecord
from rdflib import Namespace

LDP = Namespace("http://www.w3.org/ns/ldp#")


class GraphToFdpRecordMapper:
    def __init__(self, url):
        self.url = url

    def map(self, rdf_graph):
        if rdf_graph is None:
            raise ValueError("rdf_graph cannot be None")

        record = FdpRecord(self.url, rdf_graph)

        for subject, predicate, obj in rdf_graph:
            if predicate == LDP.contains:
                record.add_children(str(obj))

        return record
