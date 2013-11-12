from seantis.plonetools import setuphandlers

indexes = [
    ('first_letter', 'FieldIndex')
]


def add_catalog_indexes(context, logger=None):
    setuphandlers.add_catalog_indexes(
        'seantis.people', indexes, context, logger
    )


def import_indexes(context):
    setuphandlers.import_indexes(
        'seantis.people', indexes, context
    )
