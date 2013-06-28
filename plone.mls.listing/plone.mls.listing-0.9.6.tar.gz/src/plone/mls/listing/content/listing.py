# -*- coding: utf-8 -*-
"""Dexterity based Listing content type."""

# zope imports
from plone.directives import form
from zope import schema

# local imports
from plone.mls.listing.i18n import _


class IListing(form.Schema):
    """A single MLS Listing."""

    title = schema.TextLine(
        title=_(u'Title'),
    )

    listing_id = schema.TextLine(
        title=_(u'MLS Listing ID'),
    )
