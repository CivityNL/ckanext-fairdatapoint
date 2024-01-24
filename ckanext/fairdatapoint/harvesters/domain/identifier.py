SEPARATOR = ';'
KEY_VALUE_SEPARATOR = '='


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

        if len(key_values) > 0:
            # Get the last one, that's the one we are interested in
            key_value = key_values[-1].split(KEY_VALUE_SEPARATOR)
            if len(key_value) == 2:
                result = key_value[index]
            else:
                raise IdentifierException(
                    'Unexpected number of parts in key_value [{}]: [{}]',
                    key_values[1],
                    len(key_value)
                )
        else:
            raise IdentifierException(
                'Unexpected number of parts in record identifier [{}]: [{}]',
                self.guid,
                len(key_values)
            )

        return result
