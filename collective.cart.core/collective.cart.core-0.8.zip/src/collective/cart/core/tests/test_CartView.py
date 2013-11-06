# -*- coding: utf-8 -*-
from collective.cart.core.browser.interfaces import ICartView
from collective.cart.core.browser.view import CartView
from collective.cart.core.tests.base import IntegrationTestCase

import mock


class CartViewTestCase(IntegrationTestCase):
    """TestCase for CartView"""

    def test_subclass(self):
        from collective.cart.core.browser.view import CheckOutView
        self.assertTrue(issubclass(CartView, CheckOutView))
        from collective.cart.core.browser.interfaces import ICheckOutView
        self.assertTrue(issubclass(ICartView, ICheckOutView))

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        instance = self.create_view(CartView)
        self.assertTrue(verifyObject(ICartView, instance))

    def test_template(self):
        instance = self.create_view(CartView)
        self.assertEqual(instance.template.filename.split('/')[-1], 'base-form.pt')

    @mock.patch('collective.cart.core.browser.view.CheckOutView.__call__')
    def test___call__(self, __call__):
        instance = self.create_view(CartView)
        template = mock.Mock()
        instance.template = template
        self.assertEqual(instance(), template())
        self.assertTrue(__call__.called)
