#
# Copyright 2008, Blue Dynamics Alliance, Austria - http://bluedynamics.com
#
# GNU General Public Licence Version 2 or later

__author__ = """Robert Niederreiter <rnix@squarewave.at>"""
__docformat__ = 'plaintext'

from zope.interface import Interface
from zope.interface import implements
from zope.component import adapts

from Acquisition import Explicit

from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IBrowserView

from zope.contentprovider.interfaces import IContentProvider

from base import RequestMixin

class RendererBase(Explicit, RequestMixin):
    """An abstract content provider.
    """
    
    implements(IContentProvider)
    adapts(Interface, IBrowserRequest, IBrowserView)
    
    def __init__(self, context, request, view):
        self.__parent__ = view
        self.context = context
        self.request = request
    
    def update(self):
        raise NotImplementedError(u"Abstract base renderer does not implement "
                                  "``update()``")
    
    def render(self):
        raise NotImplementedError(u"Abstract base renderer does not implement "
                                  "``render()``")

