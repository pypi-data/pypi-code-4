from seantis.plonetools import setuphandlers

indexes = [
    ('people_uuids', 'KeywordIndex')
]


def add_catalog_indexes(context, logger=None):
    setuphandlers.add_catalog_indexes(
        'seantis.cover.people', indexes, context, logger
    )


def import_indexes(context):
    setuphandlers.import_indexes(
        'seantis.cover.people', indexes, context
    )
