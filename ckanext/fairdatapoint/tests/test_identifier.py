"""
    CKAN Fair Data Point extension Test Suite
    Copyright (C) 2024, Stichting Health-RI

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import pytest
from pytest_mock import mocker
from ckanext.fairdatapoint.harvesters.domain.identifier import Identifier, IdentifierException


class TestIdentifier:
    def test_get_part(self):
        guid = ("catalog=https://fair.healthinformationportal.eu/catalog/1c75c2c9-d2cc-44cb-aaa8-cf8c11515c8d;"
                "dataset=https://fair.healthinformationportal.eu/dataset/898ca4b8-197b-4d40-bc81-d9cd88197670")
        identifier = Identifier(guid)
        expected = "https://fair.healthinformationportal.eu/dataset/898ca4b8-197b-4d40-bc81-d9cd88197670"
        actual = identifier.get_part(1)
        assert actual == expected

    def test_get_part_zero_index(self):
        guid = ("catalog=https://fair.healthinformationportal.eu/catalog/1c75c2c9-d2cc-44cb-aaa8-cf8c11515c8d;"
                "dataset=https://fair.healthinformationportal.eu/dataset/898ca4b8-197b-4d40-bc81-d9cd88197670")
        identifier = Identifier(guid)
        expected = "dataset"
        actual = identifier.get_part(0)
        assert actual == expected

    @pytest.mark.xfail(raises=IndexError)
    def test_get_part_no_separator(self):
        with pytest.raises(IndexError):
            identifier = Identifier("some_id_no_separator")
            part = identifier.get_part(index=0)

    def test_get_part_raises(self):
        with pytest.raises(IdentifierException):
            identifier = Identifier("too_many;id_separators;in_an_id")
            part = identifier.get_part(index=1)
