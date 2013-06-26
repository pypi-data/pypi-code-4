# -*- coding: utf-8 -*-
"""Propertyshelf MLS utils."""

# python imports
from urllib import urlencode
import errno
import httplib2
import simplejson
import socket
import urllib2
# import json

# zope imports
from Acquisition import aq_inner, aq_parent
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

# local imports
from plone.mls.core.interfaces import IMLSSettings


TIMEOUT = 10


class MLSError:
    """General MLS Error."""
    def __init__(self, code=None, reason=None):
        self.code = code
        self.reason = reason


class MLSConnectionError(MLSError):
    """No Conncetion to the MLS."""


class MLSDataError(MLSError):
    """Data returned from the MLS contains errors."""


def authenticate():
    """Authenticate the Plone Website."""
    registry = getUtility(IRegistry)
    settings = registry.forInterface(IMLSSettings)
#    test_json()

    if settings.mls_site is None and settings.agency_id is None:
        return False

    url = '%(site)s/agencies/%(agency_id)s' % dict(
        site=settings.mls_site,
        agency_id=settings.agency_id,
    )
    url = urllib2.unquote(url)

    try:
        urllib2.urlopen(url)
    except IOError:
        return False

    return True


def get_language(context):
    portal_state = context.unrestrictedTraverse("@@plone_portal_state")
    return aq_inner(context).Language() or \
           aq_inner(aq_parent(context)).Language() or \
           portal_state.default_language()


def get_listing(lid, summary=False, lang=None):
    """Get the data for a single listing."""
    kwargs = {}
    registry = getUtility(IRegistry)
    settings = registry.forInterface(IMLSSettings)

    if settings.mls_site is None or len(settings.mls_site) == 0:
        raise MLSConnectionError(code=503)

    if settings.agency_id is None or len(settings.agency_id) == 0:
        raise MLSConnectionError(code=503)

    URL_BASE = '%(site)s/api/listings/listing/%(listing_id)s/agency/%' \
               '(agency_id)s' % dict(
        site=settings.mls_site,
        agency_id=settings.agency_id,
        listing_id=lid,
    )

    kwargs.update({
        'apikey': settings.mls_key,
    })

    if lang:
        kwargs.update({'lang': lang})

    if summary:
        kwargs.update({'summary': 1})

    url = URL_BASE + '?' + urlencode(kwargs)
    h = httplib2.Http(".cache")
    try:
        resp, content = h.request(url)
    except socket.error, e:
        err = 0
        if hasattr(e, 'args'):
            err = getattr(e, 'args')[0]
        else:
            err = e.errno
        if err == errno.ECONNREFUSED:  # Connection refused
            raise MLSConnectionError
    try:
        result = simplejson.loads(content)
    except simplejson.JSONDecodeError, e:
        raise MLSDataError(code=401)

    if result.get('status', 'error') != 'ok':
        raise MLSDataError
    return result.get('result', None)
