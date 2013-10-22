from seantis.plonetools import tools
from seantis.people.supermodel import (
    get_selectable_fields, get_columns, get_title_fields
)


def get_schema_columns(schema):
    columns = []

    for fields in get_columns(schema):
        columns.append(SchemaColumn(schema, fields))

    return columns


class SchemaColumn(object):

    def __init__(self, schema, fields):
        self.schema = schema
        self.fields = tools.order_fields_by_schema(fields, schema)

        self.titles = []
        for field in self.fields:
            if field in self.schema:
                self.titles.append(self.schema[field].title)
            else:
                self.titles.append(field)

        self.contains_title_field = bool(
            set(self.fields) & set(get_title_fields(self.schema))
        )
        self.selectable = (
            len(self.fields) == 1 and self.fields[0] in get_selectable_fields(
                self.schema
            )
        )
