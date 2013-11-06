# -*- coding: utf-8 -*-
from collective.cart.core.browser.interfaces import IOrderListingView
from collective.cart.core.browser.view import OrderListingView
from collective.cart.core.tests.base import IntegrationTestCase


class OrderListingViewTestCase(IntegrationTestCase):
    """TestCase for OrderListingView"""

    def test_subclass(self):
        from collective.cart.core.browser.view import BaseFormView
        self.assertTrue(issubclass(OrderListingView, BaseFormView))
        from collective.cart.core.browser.interfaces import IBaseFormView
        self.assertTrue(issubclass(IOrderListingView, IBaseFormView))

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        context = self.create_content('collective.cart.core.OrderContainer')
        instance = self.create_view(OrderListingView, context)
        self.assertTrue(verifyObject(IOrderListingView, instance))
