# -*- coding: utf-8 -*-
"""Propertyshelf MLS Embedding interfaces."""

# zope imports
from zope import schema
from zope.interface import Interface

# local imports
from plone.mls.listing.i18n import _

MSG_PRIORITY_DESCRIPTION = _(
    u'Items in this vocabulary are sorted by priority key (if available) '
    u'and value otherwise. Enter one item per line. Possible values are: %s'
)

POSSIBLE_GEOGRAPHIC_TYPES = ', '.join([
    'cloud_forest', 'dry_forest', 'highland_forest', 'rain_forest',
    'swamp_forest',
])

POSSIBLE_LISTING_TYPES = ', '.join(['cl', 'cs', 'll', 'rl', 'rs', ])

POSSIBLE_LOCATION_TYPES = ', '.join([
    'lakefront', 'mountain', 'oceanfront', 'oceanvicinity', 'riverfront',
    'rural', 'urban',
])

POSSIBLE_OBJECT_TYPES = ', '.join([
    'agricultural_land', 'apartment', 'bar_nightclub', 'commercial_condo',
    'condominium', 'construction_site', 'development_land',
    'freestanding_building', 'freestanding_villa', 'half_duplex',
    'hotel_hostel', 'house', 'medical_facility', 'mixed_use_building',
    'multi_unit_building', 'multiplex', 'office_condo', 'protected_area',
    'restaurant', 'retail_singleplex', 'strip_center_complex',
    'strip_center_unit', 'townhouse', 'warehouse',
])

POSSIBLE_OWNERSHIP_TYPES = ', '.join([
    'bank_owned', 'concession', 'fee_simple', 'fractional',
])

POSSIBLE_VIEW_TYPES = ', '.join([
    'bay_view', 'beach_view', 'city_view', 'eastern_view', 'garden_view',
    'greenbelt_view', 'lake_view', 'mountain_view', 'northern_view',
    'ocean_view', 'pond_view', 'river_view', 'southern_view', 'valley_view',
    'western_view', 'wooded_view',
])


class IMLSVocabularySettings(Interface):
    """Propertyshelf MLS settings for vocabularies.

    This describes records stored in the configuration registry and obtainable
    via plone.registry.
    """

    geographic_types_priority = schema.Text(
        description=MSG_PRIORITY_DESCRIPTION % POSSIBLE_GEOGRAPHIC_TYPES,
        required=False,
        title=_(u"'Geographic Types' priority list"),
    )

    listing_types_priority = schema.Text(
        description=MSG_PRIORITY_DESCRIPTION % POSSIBLE_LISTING_TYPES,
        required=False,
        title=_(u"'Listing Types' priority list"),
    )

    location_types_priority = schema.Text(
        description=MSG_PRIORITY_DESCRIPTION % POSSIBLE_LOCATION_TYPES,
        required=False,
        title=_(u"'Location Types' priority list"),
    )

    object_types_priority = schema.Text(
        description=MSG_PRIORITY_DESCRIPTION % POSSIBLE_OBJECT_TYPES,
        required=False,
        title=_(u"'Object Types' priority list"),
    )

    ownership_types_priority = schema.Text(
        description=MSG_PRIORITY_DESCRIPTION % POSSIBLE_OWNERSHIP_TYPES,
        required=False,
        title=_(u"'Ownership Types' priority list"),
    )

    view_types_priority = schema.Text(
        description=MSG_PRIORITY_DESCRIPTION % POSSIBLE_VIEW_TYPES,
        required=False,
        title=_(u"'View Types' priority list"),
    )


class IMLSAgencyContactInformation(Interface):
    """Propertyshelf MLS settings for custom contact information.

    This describes records stored in the configuration registry and obtainable
    via plone.registry.
    """

    use_custom_info = schema.Bool(
        default=False,
        required=False,
        title=_(
            u'Update agent information when showing a third party listing?'
        ),
    )

    agency_name = schema.TextLine(
        required=True,
        title=_(u'Agency Name'),
    )

    agency_logo_url = schema.TextLine(
        required=False,
        title=_(u'Agency Logo'),
    )

    agency_office_phone = schema.TextLine(
        required=False,
        title=_(u'Agency Office Phone'),
    )

    agency_website = schema.TextLine(
        required=False,
        title=_(u'Agency Website'),
    )

    agent_name = schema.TextLine(
        required=True,
        title=_(u'Agent Name'),
    )

    agent_title = schema.TextLine(
        required=False,
        title=_(u'Agent Title'),
    )

    agent_office_phone = schema.TextLine(
        required=False,
        title=_('Agent Office Phone'),
    )

    agent_cell_phone = schema.TextLine(
        required=False,
        title=_(u'Agent Cell Phone'),
    )

    agent_fax = schema.TextLine(
        required=False,
        title=_(u'Agent Fax'),
    )

    agent_email = schema.TextLine(
        required=True,
        title=_(u'Agent Email'),
    )
