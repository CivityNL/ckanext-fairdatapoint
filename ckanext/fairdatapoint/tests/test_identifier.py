# SPDX-FileCopyrightText: 2024 Stichting Health-RI
#
# SPDX-License-Identifier: AGPL-3.0-only

import pytest
from pytest_mock import mocker

from ckanext.fairdatapoint.harvesters.domain.identifier import (
    Identifier,
    IdentifierException,
)


class TestIdentifier:
    def test_get_part(self):
        guid = (
            "catalog=https://fair.healthinformationportal.eu/catalog/1c75c2c9-d2cc-44cb-aaa8-cf8c11515c8d;"
            "dataset=https://fair.healthinformationportal.eu/dataset/898ca4b8-197b-4d40-bc81-d9cd88197670"
        )
        identifier = Identifier(guid)
        expected = "https://fair.healthinformationportal.eu/dataset/898ca4b8-197b-4d40-bc81-d9cd88197670"
        actual = identifier.get_part(1)
        assert actual == expected

    def test_get_part_zero_index(self):
        guid = (
            "catalog=https://fair.healthinformationportal.eu/catalog/1c75c2c9-d2cc-44cb-aaa8-cf8c11515c8d;"
            "dataset=https://fair.healthinformationportal.eu/dataset/898ca4b8-197b-4d40-bc81-d9cd88197670"
        )
        identifier = Identifier(guid)
        expected = "dataset"
        actual = identifier.get_part(0)
        assert actual == expected

    def test_get_part_no_separator(self):
        with pytest.raises(IdentifierException):
            identifier = Identifier("some_id_no_separator")
            part = identifier.get_part(index=0)

    def test_get_part_raises(self):
        with pytest.raises(IdentifierException):
            identifier = Identifier("too_many;id_separators;in_an_id")
            part = identifier.get_part(index=1)

    def test_get_id_type_and_value(self):
        guid = "dataset=http://example.com/resource?id=123"
        identifier = Identifier(guid)
        assert identifier.get_id_type() == "dataset"
        assert identifier.get_id_value() == "http://example.com/resource?id=123"