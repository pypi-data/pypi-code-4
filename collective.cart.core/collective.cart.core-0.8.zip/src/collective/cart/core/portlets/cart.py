from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.cart.core import _
from collective.cart.core.interfaces import IShoppingSite
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from zope.interface import implements


class ICartPortlet(IPortletDataProvider):
    '''A portlet which can render cart content.
    '''


class Assignment(base.Assignment):
    implements(ICartPortlet)

    @property
    def title(self):
        """Title shown in @@manage-portlets"""
        return _(u"Cart")


class Renderer(base.Renderer):

    render = ViewPageTemplateFile('cart.pt')

    def cart_url(self):
        shop = IShoppingSite(self.context).shop()
        return '{}/@@cart'.format(shop.absolute_url())

    @property
    def available(self):
        if hasattr(self, 'view') and self.view.__name__ == 'cart':
            return False
        return IShoppingSite(self.context).cart_articles()

    def count(self):
        return len(self.available)


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
