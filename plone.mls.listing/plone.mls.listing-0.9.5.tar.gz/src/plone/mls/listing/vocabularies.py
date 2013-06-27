# -*- coding: utf-8 -*-
"""Vocabulary definitions."""

# zope imports
from plone.registry.interfaces import IRegistry

from zope.component import getUtility, queryMultiAdapter
from zope.globalrequest import getRequest
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

# local imports
from plone.mls.core.interfaces import IMLSSettings
from plone.mls.listing.i18n import _
from plone.mls.listing.api import search_options
from plone.mls.listing.interfaces import IMLSVocabularySettings

ROOM_VALUES = [
    ('--MINVALUE--', _(u'Min')),
    (1, '1'),
    (2, '2'),
    (3, '3'),
    (4, '4'),
    (5, '5'),
    (6, '6'),
    (7, '7'),
    (8, '8'),
    (9, '9'),
    ('--MAXVALUE--', _(u'Max')),
]

LOT_SIZE_VALUES = [
    ('--MINVALUE--', _(u'Min')),
    (500, u'500 m²'),
    (1000, u'1000 m²'),
    (2000, u'2000 m²'),
    (4000, u'4000 m²'),
    (6000, u'6000 m²'),
    (8000, u'8000 m²'),
    (10000, u'1 hec'),
    (20000, u'2 hec'),
    (100000, u'10 hec'),
    ('--MAXVALUE--', _(u'Max')),
]

INTERIOR_AREA_VALUES = [
    ('--MINVALUE--', _(u'Min')),
    (50, u'50 m²'),
    (100, u'100 m²'),
    (150, u'150 m²'),
    (250, u'250 m²'),
    (500, u'500 m²'),
    (750, u'750 m²'),
    (1000, u'1000 m²'),
    (1250, u'1250 m²'),
    (1500, u'1500 m²'),
    ('--MAXVALUE--', _(u'Max')),
]


@implementer(IVocabularyFactory)
class BasePriorityVocabulary(object):
    """Vocabulary factory with optional priority list.

    data = [
        ('x1', 'a1'),
        ('x3', 'a3'),
        ('x4', 'a4'),
        ('x2', 'a2'),
        ('x5', 'a5'),
    ]

    priority = ['x5', 'x3']

    data_sorted = [
        ('x5', 'a5'),
        ('x3', 'a3'),
        ('x1', 'a1'),
        ('x2', 'a2'),
        ('x4', 'a4'),
    ]

    def sort_data(data_arg, priority_arg):
        def get_key(item):
            if item[0] in priority_arg:
                return '__%03d' % priority_arg.index(item[0])
            return item[1]

        data_arg.sort(key=get_key)

        print data_arg
        assert data_arg == data_sorted

    sort_data(data, priority)
    """
    priority = ''
    vocabulary_name = None

    def _sort(self, data, priority):
        """Sort list of tuple by keys in priority list or value otherwise."""

        def get_key(item):
            if item[0] in priority:
                return '__0%03d' % priority.index(item[0])
            return '__1%s' % item[1]

        if len(priority) > 0:
            data.sort(key=get_key)
        else:
            data.sort(key=lambda item: item[1])

        return data

    def __call__(self, context):
        portal_state = queryMultiAdapter((context, getRequest()),
                                         name='plone_portal_state')
        registry = getUtility(IRegistry)
        try:
            settings = registry.forInterface(IMLSVocabularySettings,
                                             check=False)
        except KeyError:
            priority_list = []
        else:
            value = getattr(settings, self.priority, '')
            if value is None:
                value = ''
            priority_list = [item.strip() for item in value.split(',')
                             if len(item.strip()) > 0]

        try:
            global_settings = registry.forInterface(IMLSSettings)
        except KeyError:
            mls_url = None
        else:
            mls_url = getattr(global_settings, 'mls_site', None)

        types = search_options(mls_url, self.vocabulary_name,
                               portal_state.language())
        terms = []
        if types is not None:
            types = self._sort(types, priority_list)
            terms = [SimpleTerm(item[0], item[0], item[1]) for item in types]
        return SimpleVocabulary(terms)


class GeographicTypesVocabulary(BasePriorityVocabulary):
    """Priority sortable vocabulary factory for 'geographic_types'."""

    vocabulary_name = 'geographic_types'
    priority = 'geographic_types_priority'

GeographicTypesVocabularyFactory = GeographicTypesVocabulary()


class ListingTypesVocabulary(BasePriorityVocabulary):
    """Priority sortable vocabulary factory for 'listing_types'."""

    vocabulary_name = 'listing_types'
    priority = 'listing_types_priority'

ListingTypesVocabularyFactory = ListingTypesVocabulary()


class LocationCountyVocabulary(BasePriorityVocabulary):
    """Priority sortable vocabulary factory for 'location_county'."""

    vocabulary_name = 'location_county'

LocationCountyVocabularyFactory = LocationCountyVocabulary()


class LocationDistrictVocabulary(BasePriorityVocabulary):
    """Priority sortable vocabulary factory for 'location_district'."""

    vocabulary_name = 'location_district'

LocationDistrictVocabularyFactory = LocationDistrictVocabulary()


class LocationStateVocabulary(BasePriorityVocabulary):
    """Priority sortable vocabulary factory for 'location_state'."""

    vocabulary_name = 'location_state'

LocationStateVocabularyFactory = LocationStateVocabulary()


class LocationTypesVocabulary(BasePriorityVocabulary):
    """Priority sortable vocabulary factory for 'location_types'."""

    vocabulary_name = 'location_types'
    priority = 'location_types_priority'

LocationTypesVocabularyFactory = LocationTypesVocabulary()


class ObjectTypesVocabulary(BasePriorityVocabulary):
    """Priority sortable vocabulary factory for 'object_types'."""

    vocabulary_name = 'object_types'
    priority = 'object_types_priority'

ObjectTypesVocabularyFactory = ObjectTypesVocabulary()


class OwnershipTypesVocabulary(BasePriorityVocabulary):
    """Priority sortable vocabulary factory for 'ownership_types'."""

    vocabulary_name = 'ownership_types'
    priority = 'ownership_types_priority'

OwnershipTypesVocabularyFactory = OwnershipTypesVocabulary()


@implementer(IVocabularyFactory)
class RoomsVocabulary(object):

    def __call__(self, context):
        items = []
        for item in ROOM_VALUES:
            items.append(SimpleTerm(item[0], item[0], item[1]))
        return SimpleVocabulary(items)

RoomsVocabularyFactory = RoomsVocabulary()


class ViewTypesVocabulary(BasePriorityVocabulary):
    """Priority sortable vocabulary factory for 'view_types'."""

    vocabulary_name = 'view_types'
    priority = 'view_types_priority'

ViewTypesVocabularyFactory = ViewTypesVocabulary()


@implementer(IVocabularyFactory)
class YesNoAllVocabulary(object):

    def __call__(self, context):
        items = []
        items.append(SimpleTerm('1', '1', _(u'Yes')))
        items.append(SimpleTerm('0', '0', _(u'No')))
        items.append(SimpleTerm('--NOVALUE--', '--NOVALUE--', _(u'All')))
        return SimpleVocabulary(items)

YesNoAllVocabularyFactory = YesNoAllVocabulary()


@implementer(IVocabularyFactory)
class LotSizeVocabulary(object):

    def __call__(self, context):
        items = []
        for item in LOT_SIZE_VALUES:
            items.append(SimpleTerm(item[0], item[0], item[1]))
        return SimpleVocabulary(items)

LotSizeVocabularyFactory = LotSizeVocabulary()


@implementer(IVocabularyFactory)
class InteriorAreaVocabulary(object):

    def __call__(self, context):
        items = []
        for item in INTERIOR_AREA_VALUES:
            items.append(SimpleTerm(item[0], item[0], item[1]))
        return SimpleVocabulary(items)

InteriorAreaVocabularyFactory = InteriorAreaVocabulary()
