# -*- coding: utf-8 -*-
from collective.cart.core.browser.interfaces import ICheckOutView
from collective.cart.core.browser.view import CheckOutView
from collective.cart.core.tests.base import IntegrationTestCase

import mock


class CheckOutViewTestCase(IntegrationTestCase):
    """TestCase for CheckOutView"""

    def test_subclass(self):
        from collective.cart.core.browser.view import BaseFormView
        self.assertTrue(issubclass(CheckOutView, BaseFormView))
        from collective.cart.core.browser.interfaces import IBaseFormView
        self.assertTrue(issubclass(ICheckOutView, IBaseFormView))

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        instance = self.create_view(CheckOutView)
        self.assertTrue(verifyObject(ICheckOutView, instance))

    @mock.patch('collective.cart.core.browser.view.IShoppingSite')
    def test___call__(self, IShoppingSite):
        instance = self.create_view(CheckOutView)
        instance.request = mock.Mock()
        self.assertIsNone(instance())
        instance.request.set.assert_called_with('disable_border', True)
        self.assertEqual(IShoppingSite().clean_articles_in_cart.call_count, 1)
