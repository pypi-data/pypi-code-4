# -*- coding: utf-8 -*-
"""Article Provider."""

# zope imports
from Products.CMFCore.utils import getToolByName
from raptus.article.core.interfaces import IArticle
from zope.component import adapts
from zope.interface import implements


# local imports
from plone.mls.listing.article.interfaces import IListingLists


class ListingLists(object):
    """Provider for listings contained in an article."""
    implements(IListingLists)
    adapts(IArticle)

    def __init__(self, context):
        self.context = context

    def getListingLists(self, **kwargs):
        """Returns a list of listings (catalog brains)."""
        catalog = getToolByName(self.context, 'portal_catalog')
        return catalog(
            portal_type='plone.mls.listing.listing',
            path={
                'query': '/'.join(self.context.getPhysicalPath()),
                'depth': 1,
            },
            sort_on='getObjPositionInParent', **kwargs)
