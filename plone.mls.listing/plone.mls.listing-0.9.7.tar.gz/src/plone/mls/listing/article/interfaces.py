# -*- coding: utf-8 -*-
"""Article related interfaces."""

# zope imports
from zope.interface import Interface


class IListingLists(Interface):
    """Provider for listings contained in an article."""

    def getListingLists(**kwargs):
        """Returns a list of listings (catalog brains)."""
