# -*- coding: utf-8 -*-
"""View adapter."""

# plone imports
from z3c.form.widget import StaticWidgetAttribute

# local imports
from plone.mls.listing import browser
from plone.mls.listing.i18n import _

PleaseSelectLCC = StaticWidgetAttribute(
    _(u'All'), view=browser.listing_collection.ListingCollectionConfiguration)
PleaseSelectLSF = StaticWidgetAttribute(
    _(u'All'), view=browser.listing_search.ListingSearchForm)
PleaseSelectRLC = StaticWidgetAttribute(
    _(u'All'), view=browser.recent_listings.RecentListingsConfiguration)


PleaseSelectState = StaticWidgetAttribute(
    _(u'All'), field=browser.listing_search.IListingSearchForm['location_state'])
PleaseSelectCounty = StaticWidgetAttribute(
    _(u'All'), field=browser.listing_search.IListingSearchForm['location_county'])
PleaseSelectDistrict = StaticWidgetAttribute(
    _(u'All'), field=browser.listing_search.IListingSearchForm['location_district'])
