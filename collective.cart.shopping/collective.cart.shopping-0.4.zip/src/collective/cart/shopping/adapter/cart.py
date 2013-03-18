from Products.CMFCore.interfaces import ISiteRoot
from collective.behavior.price.interfaces import ICurrency
from collective.behavior.size.interfaces import ISize
from collective.cart.core.adapter.cart import CartAdapter as BaseCartAdapter
from collective.cart.shipping.interfaces import ICartShippingMethod
from collective.cart.shopping.interfaces import IArticleAdapter
from collective.cart.shopping.interfaces import ICart
from collective.cart.shopping.interfaces import ICartAdapter
from collective.cart.shopping.interfaces import ICartArticle
from collective.cart.shopping.interfaces import ICartArticleAdapter
from collective.cart.shopping.interfaces import ICustomerInfo
from decimal import Decimal
from five import grok
from moneyed import Money
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class CartAdapter(BaseCartAdapter):
    """Adapter for Cart"""

    grok.context(ICart)
    grok.provides(ICartAdapter)

    @property
    def articles(self):
        """List of dictionary of Articles within cart."""
        encoding = getUtility(ISiteRoot).getProperty('email_charset', 'utf-8')
        res = []
        for item in self.get_content_listing(ICartArticle):
            obj = item.getObject()
            items = {
                'description': item.Description().decode(encoding),
                'gross': item.gross,
                'gross_subtotal': ICartArticleAdapter(obj).gross_subtotal,
                'image_url': None,
                'obj': obj,
                'quantity': item.quantity,
                'sku': item.sku,
                'title': item.Title().decode(encoding),
                'url': None,
                'vat_rate': item.vat_rate,
            }
            orig_article = ICartArticleAdapter(obj).orig_article
            if orig_article:
                items['url'] = orig_article.absolute_url()
                items['image_url'] = IArticleAdapter(orig_article).image_url
            res.append(items)
        return res

    @property
    def articles_total(self):
        """Total money of articles"""
        registry = getUtility(IRegistry)
        currency = registry.forInterface(ICurrency).default_currency
        res = Money(0.00, currency=currency)
        for item in self.articles:
            res += item['gross'] * item['quantity']
        return res

    @property
    def total(self):
        total = self.articles_total
        if self.shipping_gross_money:
            total += self.shipping_gross_money
        return total

    @property
    def shipping_method(self):
        """Brain of shipping method of the cart."""
        return self.get_brain(ICartShippingMethod, depth=1)

    def _calculated_weight(self, rate=None):
        weight = 0
        for article in self.articles:
            obj = article['obj']
            weight += ISize(obj).calculated_weight(rate=rate) * article['quantity']
        return weight

    @property
    def shipping_gross_money(self):
        registry = getUtility(IRegistry)
        currency = registry.forInterface(ICurrency).default_currency
        if self.shipping_method:
            return self.shipping_method.gross
        return Money(Decimal('0.00'), currency)

    @property
    def shipping_net_money(self):
        registry = getUtility(IRegistry)
        currency = registry.forInterface(ICurrency).default_currency
        if self.shipping_method:
            return self.shipping_method.net
        return Money(Decimal('0.00'), currency)

    @property
    def shipping_vat_money(self):
        registry = getUtility(IRegistry)
        currency = registry.forInterface(ICurrency).default_currency
        if self.shipping_method:
            return self.shipping_method.vat
        return Money(Decimal('0.00'), currency)

    def get_address(self, name):
        """Get address by name."""
        if name == 'shipping' and self.context.billing_same_as_shipping:
            name = 'billing'
        return self.get_brain(ICustomerInfo, query=1, id=name)
