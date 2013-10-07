from zope.component import adapts
from Products.CMFPlone.interfaces.syndication import IFeed
from plone.dexterity.interfaces import IDexterityContent
from plone.rfc822.interfaces import IPrimaryFieldInfo
from Products.CMFPlone.browser.syndication.adapters import DexterityItem


class DItem(DexterityItem):
    adapts(IDexterityContent, IFeed)

    def __init__(self, context, feed):
        super(DexterityItem, self).__init__(context, feed)
        self.dexterity = IDexterityContent.providedBy(context)
        try:
            self.primary = IPrimaryFieldInfo(self.context, None)
        except TypeError:
            self.primary = None