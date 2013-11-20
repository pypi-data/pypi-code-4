# -*- coding: utf-8 -*-
from plone import api
from plone.indexer import indexer

from seantis.plonetools import tools

from seantis.people.interfaces import IPerson, IPersonMarker
from seantis.people.supermodel import (
    get_selectable_fields, get_order, get_columns
)


def get_sortable_title_text(obj):
    schema = tools.get_schema_from_portal_type(obj.portal_type)
    order = list(get_order(schema))

    if order:
        title = u' '.join((getattr(obj, field, u'') for field in order))
        title = title.strip()

    if not order or not title:
        title = getattr(obj, 'title', u'')

    return title.strip()


@indexer(IPersonMarker)
def sortable_title(obj):
    return tools.unicode_collate_sortkey()(get_sortable_title_text(obj))


@indexer(IPersonMarker)
def first_letter(obj):
    title = get_sortable_title_text(obj)
    return title and title[:1].upper() or u''


def on_type_modified(fti, event=None):
    """ The IPerson types need to be reindexed if the type changes, because
    the supermodel could be different and it's hints may have an effect on
    the metadata/indexes.

    """

    update_related_indexes(fti)


def update_related_indexes(fti):

    if IPerson.__identifier__ not in fti.behaviors:
        return

    update_metadata(fti)

    catalog = api.portal.get_tool('portal_catalog')
    new_indexes = update_selectable_field_indexes(fti)

    if new_indexes:
        for new_index in new_indexes:
            catalog.reindexIndex(new_index, REQUEST=None)

    for brain in catalog(portal_type=fti.id):
        brain.getObject().reindexObject(
            idxs=['sortable_title', 'first_letter']
        )


def get_selectable_prefix(portal_type):
    return portal_type + '_selectable_'


def get_selectable_field_ix(portal_type, field):
    return get_selectable_prefix(portal_type) + field


def get_selectable_field_indexes(fti):
    prefix = get_selectable_prefix(fti.id)
    zcatalog = api.portal.get_tool('portal_catalog')._catalog
    return [ix for ix in zcatalog.indexes if ix.startswith(prefix)]


def update_metadata(fti):
    for column in get_columns(fti.lookupSchema()):
        for field in column:
            tools.add_attribute_to_metadata(field)


def update_selectable_field_indexes(fti):
    catalog = api.portal.get_tool('portal_catalog')
    fields = get_selectable_fields(fti.lookupSchema())

    new_indexes = []

    # remove the indexes which are no longer used
    prefix = get_selectable_prefix(fti.id)
    for ix in get_selectable_field_indexes(fti):
        field = ix.replace(prefix, '')

        if field not in fields:
            catalog.delIndex(ix)

    # add the indexes which are not yet defined
    for field in fields:
        index_name = get_selectable_field_ix(fti.id, field)
        if index_name not in catalog.indexes():
            catalog.addIndex(index_name, 'KeywordIndex', extra={
                'indexed_attrs': field
            })
            new_indexes.append(index_name)

    return new_indexes
