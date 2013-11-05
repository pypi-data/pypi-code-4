from seantis.plonetools import tools
from seantis.people.supermodel.security import has_read_access
from seantis.people.supermodel import (
    get_selectable_fields, get_columns, get_title_fields
)


def unrestricted_get_schema_columns(schema):
    return _get_schema_columns(schema, None, restricted=False)


def get_schema_columns(schema, context):
    return _get_schema_columns(schema, context, restricted=True)


def _get_schema_columns(schema, context, restricted):
    columns = []

    for fields in get_columns(schema):
        if restricted:
            fields = [
                f for f in fields if has_read_access(schema, f, context)
            ]

        if fields:
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
