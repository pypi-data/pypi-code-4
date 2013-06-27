"""This module add a UUID converter for werkzeug routing."""

from werkzeug.routing import BaseConverter


class UuidConverter(BaseConverter):
    """This converter matches UUIDs."""

    def __init__(self, url_map,):
        super(UuidConverter, self).__init__(url_map)
        self.regex = ('[A-Fa-f0-9]{8}-'
                      '[A-Fa-f0-9]{4}-'
                      '4[A-Fa-f0-9]{3}-'
                      '(:?8|9|A|B|a|b)[A-Fa-f0-9]{3}-'
                      '[A-Fa-f0-9]{12}')

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value
