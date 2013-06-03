################################################################
# vs.org (C) 2011, Veit Schiele
################################################################

# $Id$

from zope.interface import implements

from Products.Five.browser import BrowserView
from plone.memoize.instance import memoize

from interfaces import IMapView
from ..interfaces import IAddressProvider


class MapView(BrowserView):
    """ Google Maps integration """

    def __init__(self, context, request):
        self.context = context
        self.request = request
                                
    def getAddresses(self):
        """ Provide the addresses of the current object (requires
            to implement IAddressProvider.
        """
        adapter = IAddressProvider(self.context)
        return adapter.getAddresses()
