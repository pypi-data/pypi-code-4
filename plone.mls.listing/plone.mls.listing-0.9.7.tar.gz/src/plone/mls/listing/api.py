# -*- coding: utf-8 -*-
"""MLS API utility methods."""

# python imports
from DateTime import DateTime
import logging
import time

# zope imports
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

# local imports
from mls.apiclient.client import ListingResource
from mls.apiclient.exceptions import MLSError
from plone.mls.core.interfaces import IMLSSettings
from plone.mls.listing import PRODUCT_NAME


logger = logging.getLogger(PRODUCT_NAME)
# Store the options here (which means in RAM)
OPTIONS_CACHE = {}  # language_category: ({date, language, category, itemlist})


def prepare_search_params(data):
    """Prepare search params."""
    params = {}

    for item in data:
        if item in ['baths', 'beds', 'lot_size', 'interior_area']:
            min_max = data[item]
            if isinstance(min_max, (list, tuple, )):
                if len(min_max) > 0 and min_max[0] != '--MINVALUE--':
                    params[item + '_min'] = min_max[0]
                if len(min_max) > 1 and min_max[1] != '--MAXVALUE--':
                    params[item + '_max'] = min_max[1]
                continue

        # Convert lists and tuples to comma separated lists.
        if isinstance(data[item], (list, tuple, )):
            if len(data.get(item, ())) > 0:
                data[item] = ','.join(data[item])
            else:
                data[item] = None

        # Remove all None-Type values.
        if data[item] is not None:
            value = data[item]
            if isinstance(value, unicode):
                value = value.encode("utf-8")
            params[item] = value
    return params


class SearchOptions(object):
    """Cached search options."""

    # time in minutes after which we retry to load it after a failure
    FAILURE_DELAY = 10
    category = None
    language = None
    timeout = 100

    def __init__(self, category, language, timeout):
        self.category = category
        self.language = language
        self.timeout = timeout

        self._items = []
        self._loaded = False  # Is the category already loaded?
        self._failed = False  # Does it fail with the last update?
        self._last_update_time_in_minutes = 0  # When was the last update?
        self._last_update_time = None  # Time as DateTime or Now.

    @property
    def last_update_time_in_minutes(self):
        """return the time the last update was done in minutes"""
        return self._last_update_time_in_minutes

    @property
    def last_update_time(self):
        """return the time the last update was done in minutes"""
        return self._last_update_time

    @property
    def update_failed(self):
        return self._failed

    @property
    def ok(self):
        return (not self._failed and self._loaded)

    @property
    def loaded(self):
        """return whether this feed is loaded or not"""
        return self._loaded

    @property
    def needs_update(self):
        """check if this feed needs updating"""
        now = time.time() / 60
        return (self.last_update_time_in_minutes + self.timeout) < now

    def update(self):
        """update this feed"""
        now = time.time() / 60

        # check for failure and retry
        if self.update_failed:
            if (self.last_update_time_in_minutes + self.FAILURE_DELAY) < now:
                return self._retrieveCategory()
            else:
                return False

        # check for regular update
        if self.needs_update:
            return self._retrieveCategory()

        return self.ok

    def _retrieveCategory(self):
        """do the actual work and try to retrieve the feed"""
        if self.category is not None:
            self._last_update_time_in_minutes = time.time() / 60
            self._last_update_time = DateTime()
            registry = getUtility(IRegistry)
            settings = registry.forInterface(IMLSSettings)
            base_url = getattr(settings, 'mls_site', None)
            api_key = getattr(settings, 'mls_key', None)
            resource = ListingResource(base_url, api_key=api_key)
            results = []
            try:
                results = resource.category(self.category, self.language)
            except MLSError, e:
                self._loaded = True  # we tried at least but have a failed load
                self._failed = True
                logger.warn(e)
                return False
            self._items = results
            self._loaded = True
            self._failed = False
            return True
        self._loaded = True
        self._failed = True  # no url set means failed
        return False  # no url set, although that should not really happen

    @property
    def items(self):
        return self._items


def search_options(mls_url, category, lang=None):
    if mls_url is None or len(mls_url) < 1:
        return

    timeout = 60
    key = mls_url + category + '_' + lang
    options = OPTIONS_CACHE.get(key, None)

    if options is None:
        options = SearchOptions(category, lang, timeout)

        if options.update():
            OPTIONS_CACHE[key] = options
    else:
        options.update()

    return options.items


def recent_listings(params={}, batching=True):
    """Return a list of recent MLS listings."""
    search_params = {
        'sort_on': 'created',
        'reverse': '1',
    }
    search_params.update(params)
    registry = getUtility(IRegistry)
    settings = registry.forInterface(IMLSSettings)
    base_url = getattr(settings, 'mls_site', None)
    api_key = getattr(settings, 'mls_key', None)
    batch = None
    results = []
    resource = ListingResource(base_url, api_key=api_key)

    try:
        results, batch = resource.search(search_params)
    except MLSError, e:
        logger.warn(e)

    if batching:
        return results, batch
    return results


def listing_details(listing_id, lang=None):
    """Return detail information for a listing."""
    registry = getUtility(IRegistry)
    settings = registry.forInterface(IMLSSettings)
    base_url = getattr(settings, 'mls_site', None)
    api_key = getattr(settings, 'mls_key', None)
    resource = ListingResource(base_url, api_key=api_key)
    try:
        listing = resource.get(listing_id, lang=lang)
    except MLSError, e:
        logger.warn(e)
        return None
    return listing.get('listing', None)


def search(params={}, batching=True):
    """Search for listings."""
    search_params = {
        'sort_on': 'created',
        'reverse': '1',
    }
    search_params.update(params)
    registry = getUtility(IRegistry)
    settings = registry.forInterface(IMLSSettings)
    base_url = getattr(settings, 'mls_site', None)
    api_key = getattr(settings, 'mls_key', None)
    batch = None
    results = []
    resource = ListingResource(base_url, api_key=api_key)

    try:
        results, batch = resource.search(search_params)
    except MLSError, e:
        logger.warn(e)

    if batching:
        return results, batch
    return results
