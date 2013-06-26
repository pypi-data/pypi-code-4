# -*- coding: utf-8 -*-
"""Interface definitions."""

# zope imports
from plone.theme.interfaces import IDefaultPloneLayer
from zope.interface import Interface


class IListingSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer."""


class IListingDetails(Interface):
    """Marker interface for ListingDetails view."""


class IBaseListingItems(Interface):
    """Marker interface for all listing 'collection' items."""
