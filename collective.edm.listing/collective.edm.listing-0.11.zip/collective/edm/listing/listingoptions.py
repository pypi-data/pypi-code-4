from zope.interface import implements
from zope.component import adapts

from collective.edm.listing.interfaces import IEDMListingOptions, IEDMListing
from zope.interface.interface import Interface


class DefaultListingOptions(object):
    implements(IEDMListingOptions)
    adapts(Interface, Interface, IEDMListing)
    
    sort_mode = 'manual'
    default_sort_on = False
    default_sort_order = 'asc'
    allow_edit_popup = True
    content_filter = None
    
    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.view = view