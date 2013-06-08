from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.base.interfaces import IRepeatedViewletManager
from plone.app.viewletmanager.manager import OrderedViewletManager
from zope.interface import implements
from zope.viewlet.manager import ViewletManagerBase


class RepeatedViewletManager(OrderedViewletManager, ViewletManagerBase):
    """Viewlet manager for passing object to viewlets repeatedly."""
    implements(IRepeatedViewletManager)
    template = ViewPageTemplateFile('viewletmanagers/repeated-viewlet-manager.pt')

    def items(self):
        """Returns list

        :rtype: list
        """
        raise NotImplementedError('Return list')
