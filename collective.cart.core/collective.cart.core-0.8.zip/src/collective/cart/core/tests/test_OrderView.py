# -*- coding: utf-8 -*-
from collective.cart.core.browser.interfaces import IOrderView
from collective.cart.core.browser.view import OrderView
from collective.cart.core.tests.base import IntegrationTestCase

import mock


class OrderViewTestCase(IntegrationTestCase):
    """TestCase for OrderView"""

    def test_subclass(self):
        from Products.Five import BrowserView
        self.assertTrue(issubclass(OrderView, BrowserView))
        from collective.base.interfaces import IBaseFormView
        self.assertTrue(issubclass(IOrderView, IBaseFormView))

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        instance = self.create_view(OrderView)
        self.assertTrue(verifyObject(IOrderView, instance))

    def test_title(self):
        order = self.create_content('collective.cart.core.Order', id='2')
        instance = self.create_view(OrderView, order)
        self.assertEqual(instance.title(), u'order_view_title')

    def test_description(self):
        order = self.create_content('collective.cart.core.Order', id='2', description="Descriptiön")
        instance = self.create_view(OrderView, order)
        self.assertEqual(instance.description(), 'Descriptiön')

    def test___call__(self):
        instance = self.create_view(OrderView)
        template = mock.Mock()
        instance.template = template
        self.assertEqual(instance(), template())
