# -*- coding: utf-8 -*-
from collective.cart.core.browser.viewlet import AddToCartViewlet
from collective.cart.core.tests.base import IntegrationTestCase
from collective.cart.core.browser.interfaces import IAddToCartViewlet

import mock


class AddToCartViewletTestCase(IntegrationTestCase):
    """TestCase for AddToCartViewlet"""

    def test_subclass(self):
        from plone.app.layout.viewlets.common import ViewletBase
        self.assertTrue(issubclass(AddToCartViewlet, ViewletBase))
        from collective.cart.core.browser.interfaces import IViewlet
        self.assertTrue(issubclass(IAddToCartViewlet, IViewlet))

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        article = self.create_content('collective.cart.core.Article')
        instance = self.create_viewlet(AddToCartViewlet, article)
        self.assertTrue(verifyObject(IAddToCartViewlet, instance))

    def test_index(self):
        article = self.create_content('collective.cart.core.Article', id='1')
        instance = self.create_viewlet(AddToCartViewlet, article)
        self.assertEqual(instance.index.filename.split('/')[-1], 'add-to-cart.pt')

    @mock.patch('collective.cart.core.browser.viewlet.IArticleAdapter')
    def test_available(self, IArticleAdapter):
        article = self.create_content('collective.cart.core.Article', id='1')
        instance = self.create_viewlet(AddToCartViewlet, article)
        IArticleAdapter().addable_to_cart.return_value = 'AVAILABLE'
        self.assertEqual(instance.available(), 'AVAILABLE')

    @mock.patch('collective.cart.core.browser.viewlet.IArticleAdapter')
    def test_update(self, IArticleAdapter):
        article = self.create_content('collective.cart.core.Article', id='1')
        instance = self.create_viewlet(AddToCartViewlet, article)
        instance.request = mock.Mock()
        instance.request.form = {}
        self.assertIsNone(instance.update())
        self.assertFalse(IArticleAdapter().add_to_cart.called)
        self.assertFalse(instance.request.response.redirect.called)

        instance.request.form = {'form.buttons.AddToCart': True}
        from zExceptions import Forbidden
        with self.assertRaises(Forbidden):
            instance.update()

        instance.context.restrictedTraverse = mock.Mock()
        instance.context.restrictedTraverse().current_base_url.return_value = 'CURRENT_BASE_URL'
        self.assertIsNotNone(instance.update())
        self.assertTrue(IArticleAdapter().add_to_cart.called)
        instance.request.response.redirect.assert_called_with('CURRENT_BASE_URL')
