import logging
log = logging.getLogger('seantis.people')

from collections import namedtuple

import tablib

from plone import api

from zope.schema import getFields, getValidationErrors
from zope.schema.interfaces import (
    IFromUnicode, ValidationError, SchemaNotFullyImplemented
)

from seantis.people import _
from seantis.people.errors import ContentImportError
from seantis.plonetools import tools

supported_formats = ('csv', )


def import_people(request, container, portal_type, format, data):
    dataset = get_dataset(format, data)
    attribute_map = get_attribute_map(request, dataset.headers, portal_type)

    schema = tools.get_schema_from_portal_type(portal_type)

    for ix, record in enumerate(dataset.dict):
        try:
            values = get_attribute_values(record, attribute_map)

            # add None for missing values
            for field in getFields(schema).keys():
                if field not in values:
                    values[field] = None

            validate_attribute_values(schema, values)

            api.content.create(
                container=container,
                type=portal_type,
                id='',
                **values
            )
        except ContentImportError, e:
            raise ContentImportError(
                e.message, rownumber=ix+1, colname=e.colname
            )
        except Exception, e:
            log.exception('error importing people')
            raise ContentImportError(e.message, rownumber=ix+1)

    return ix + 1


def get_dataset(format, data):
    assert format in supported_formats

    def get_dataset_from_csv():
        ds = tablib.Dataset()
        ds.csv = data

        return ds

    return locals()['get_dataset_from_{}'.format(format)]()


def get_attribute_map(request, headers, portal_type):

    if not headers:
        raise ContentImportError(_(u'No column headers were found'))

    schema = tools.get_schema_from_portal_type(portal_type)
    attribute_map = {}

    fields = getFields(schema)

    known_titles = dict((field.title, field) for field in fields.values())
    known_fields = dict((key, field) for key, field in fields.items())

    translate = tools.translator(request)
    known_translated_titles = dict(
        (translate(field.title), field) for field in fields.values()
    )

    for header in headers:

        if header in known_translated_titles:
            field = known_translated_titles[header]
        elif header in known_fields:
            field = known_fields[header]
        elif header in known_titles:
            field = known_titles[header]
        else:
            continue

        if field in attribute_map.values():
            raise ContentImportError(
                _(
                    u'The ${name} column is specified more than once',
                    mapping=dict(name=header)
                )
            )

        if field in ('title', 'id'):
            raise ContentImportError(
                _(
                    u'The ${name} column is invalid. "title" and "id" are '
                    u'reserved fieldnames which may not be used.',
                    mapping=dict(name=header)
                )
            )

        attribute_map[header] = field

    return attribute_map


def get_attribute_values(record, attribute_map):
    values = {}

    for header, field in attribute_map.items():

        assert IFromUnicode.providedBy(field), """
            {} does not support fromUnicode
        """.format(field)

        try:
            values[field.__name__] = field.fromUnicode(record[header])
        except ValidationError, e:
            raise ContentImportError(e.doc(), colname=header)
        except ValueError, e:
            raise ContentImportError(e.message, colname=header)

    return values


def validate_attribute_values(schema, values):
    obj = namedtuple('ImportObject', values.keys())(**values)

    for error in getValidationErrors(schema, obj):
        column = schema[error[0]].title

        if isinstance(error[1], SchemaNotFullyImplemented):
            raise ContentImportError(
                _(u'Required column is missing'), colname=column
            )
        else:
            raise ContentImportError(error[1].message, colname=column)
