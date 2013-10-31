#
# Copyright 2008, Blue Dynamics Alliance, Austria - http://bluedynamics.com
#
# GNU General Public Licence Version 2 or later

__author__ = """Robert Niederreiter <rnix@squarewave.at>"""
__docformat__ = 'plaintext'

from zope.interface import Interface
from zope.interface import implements
from zope.component import adapts
from zope.component import getAdapters
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.app.publisher.interfaces.browser import IBrowserMenu
from zope.app.publisher.browser.menu import BrowserMenu
from zope.app.publisher.browser.menu import BrowserMenuItem

from base import RequestMixin

class MenuBase(BrowserMenu):
    """Abstract BrowserMenu implementation.
    """
    implements(IBrowserMenu)
    
    def __init__(self, id, title=u'', description=u''):
        self.id = id
        self.title = title
        self.description = description
    
    def _getMenuItems(self, object, request, iface):
        """TODO: think wether availability should be checked here or not.
        
        @param object: the lookup context
        @param request: the request
        @param iface: the menu item interface to lookup
        @return: list containing IBrowserMenuItem implementing instances
        """
        adapters = getAdapters((object, request), iface)
        items = list()
        for adapter in adapters:
            items.append(adapter[1])
        items.sort(cmp=lambda x, y: x.order > y.order and 1 or -1)
        return items

class MenuItemBase(BrowserMenuItem, RequestMixin):
    """Abstract base menu item.
    """
    adapts(Interface, IBrowserRequest)
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.description = ''
    
    @property
    def title(self):
        raise NotImplementedError(u"Abstract IntegralMenuItem does not "
                                  "implement ``title``")
    
    @property
    def action(self):
        raise NotImplementedError(u"Abstract IntegralMenuItem does not "
                                  "implement ``action``")
    
    def available(self):
        raise NotImplementedError(u"Abstract IntegralMenuItem does not "
                                  "implement ``available()``")
    
    @property
    def icon(self):
        return None
    
    def selected(self):
        return False