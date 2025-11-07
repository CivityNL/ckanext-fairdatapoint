# SPDX-FileCopyrightText: 2023 Civity
# SPDX-FileContributor: 2024 Stichting Health-RI
#
# SPDX-License-Identifier: AGPL-3.0-only

SEPARATOR = ";"
KEY_VALUE_SEPARATOR = "="


class IdentifierException(Exception):
    pass

class Identifier:

    def __init__(self, guid: str):
        self.guid: str = guid

    def add(self, id_type: str, id_value: str):
        if len(self.guid) > 0:
            self.guid += SEPARATOR

        self.guid += id_type + KEY_VALUE_SEPARATOR + id_value

    def get_id_type(self) -> str:
        return self.get_part(0)

    def get_id_value(self) -> str:
        return self.get_part(1)

    def get_part(self, index: int) -> str:
        key_values = self.guid.split(SEPARATOR)

        if not self.guid.strip() or key_values == ['']:
            raise IdentifierException(
                f"Empty or improperly formatted record identifier: [{self.guid}]"
            )

        key_value = key_values[-1].split(KEY_VALUE_SEPARATOR, 1)

        if len(key_value) != 2:
            raise IdentifierException(
                f"Unexpected number of parts in key_value [{key_values[-1]}]: [{len(key_value)}]"
            )

        return key_value[index]

