from zope.interface import implements
from zope.component import getUtility
from Products.Five.browser import BrowserView
from Acquisition import aq_inner

from .interfaces.browser import IConnectBrowserView
from ..interfaces.utility import IConnect

class ConnectBrowserView(BrowserView):
    """Connect Browser View"""
    implements(IConnectBrowserView)

    def upload(self):
        """Upload a file to the zodb"""

        context = aq_inner(self.context)
        object = IUpload(self.context)
        return object.upload()

    def save(self, text, fieldname):
        """Saves the specified richedit field"""

        context = aq_inner(self.context)
        object = ISave(self.context)
        return object.save(text, fieldname)
