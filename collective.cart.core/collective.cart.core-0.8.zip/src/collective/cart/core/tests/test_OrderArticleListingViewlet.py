# -*- coding: utf-8 -*-
from collective.cart.core.browser.interfaces import IOrderArticleListingViewlet
from collective.cart.core.browser.viewlet import OrderArticleListingViewlet
from collective.cart.core.tests.base import IntegrationTestCase


class OrderArticleListingViewletTestCase(IntegrationTestCase):
    """TestCase for OrderArticleListingViewlet"""

    def test_subclass(self):
        from plone.app.layout.viewlets.common import ViewletBase
        self.assertTrue(issubclass(OrderArticleListingViewlet, ViewletBase))
        from collective.cart.core.browser.interfaces import IViewlet
        self.assertTrue(issubclass(IOrderArticleListingViewlet, IViewlet))

    def test_verifyObject(self):
        from collective.cart.core.browser.interfaces import IOrderArticleListingViewlet
        from zope.interface.verify import verifyObject
        instance = self.create_viewlet(OrderArticleListingViewlet)
        self.assertTrue(verifyObject(IOrderArticleListingViewlet, instance))
