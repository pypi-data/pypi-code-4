# -*- coding: utf-8 -*-
from collective.cart.core.browser.interfaces import ICartArticleListingViewlet
from collective.cart.core.browser.viewlet import CartArticleListingViewlet
from collective.cart.core.interfaces import IShoppingSiteRoot
from collective.cart.core.tests.base import IntegrationTestCase
from zope.interface import alsoProvides

import mock


class CartArticleListingViewletTestCase(IntegrationTestCase):
    """TestCase for CartArticleListingViewlet"""

    def test_subclass(self):
        from plone.app.layout.viewlets.common import ViewletBase
        self.assertTrue(issubclass(CartArticleListingViewlet, ViewletBase))
        from collective.cart.core.browser.interfaces import IViewlet
        self.assertTrue(issubclass(ICartArticleListingViewlet, IViewlet))

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        instance = self.create_viewlet(CartArticleListingViewlet)
        self.assertTrue(verifyObject(ICartArticleListingViewlet, instance))

    def test_index(self):
        alsoProvides(self.portal, IShoppingSiteRoot)
        instance = self.create_viewlet(CartArticleListingViewlet)
        self.assertEqual(instance.index.filename.split('/')[-1], 'cart-article-listing.pt')

    @mock.patch('collective.cart.core.browser.viewlet.IShoppingSite')
    def test_articles(self, IShoppingSite):
        alsoProvides(self.portal, IShoppingSiteRoot)
        instance = self.create_viewlet(CartArticleListingViewlet)
        self.assertEqual(instance.articles(), IShoppingSite().cart_article_listing())

    @mock.patch('collective.cart.core.browser.viewlet.IShoppingSite')
    def test_update(self, IShoppingSite):
        alsoProvides(self.portal, IShoppingSiteRoot)
        instance = self.create_viewlet(CartArticleListingViewlet)
        instance.request = mock.Mock()
        instance.request.form = {}
        self.assertIsNone(instance.update())
        self.assertEqual(IShoppingSite().remove_cart_articles.call_count, 0)
        self.assertEqual(instance.request.response.redirect.call_count, 0)

        instance.request = mock.Mock()
        instance.request.form = {'form.buttons.RemoveArticle': 'UUID'}
        from zExceptions import Forbidden
        with self.assertRaises(Forbidden):
            instance.update()

        instance.context.restrictedTraverse = mock.Mock()
        instance.context.restrictedTraverse().current_base_url.return_value = 'CURRENT_BASE_URL'
        self.assertIsNone(instance.update())
        self.assertEqual(IShoppingSite().remove_cart_articles.call_count, 1)
        IShoppingSite().remove_cart_articles.assert_called_with('UUID')
        self.assertEqual(instance.request.response.redirect.call_count, 0)

        IShoppingSite().cart_articles.return_value = {}
        self.assertIsNotNone(instance.update())
        self.assertEqual(IShoppingSite().remove_cart_articles.call_count, 2)
        IShoppingSite().remove_cart_articles.assert_called_with('UUID')
        self.assertEqual(instance.request.response.redirect.call_count, 1)
        instance.request.response.redirect.assert_called_with('CURRENT_BASE_URL')
