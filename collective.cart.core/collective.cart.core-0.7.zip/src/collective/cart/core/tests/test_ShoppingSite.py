# -*- coding: utf-8 -*-
from collective.cart.core.adapter.interface import ShoppingSite
from collective.cart.core.interfaces import IShoppingSite
from collective.cart.core.interfaces import IShoppingSiteRoot
from collective.cart.core.tests.base import IntegrationTestCase
from zope.interface import alsoProvides
from zope.interface import noLongerProvides

import mock


class ShoppingSiteTestCase(IntegrationTestCase):
    """TestCase for ShoppingSite"""

    def test_subclass(self):
        from collective.base.adapter import Adapter
        self.assertTrue(issubclass(ShoppingSite, Adapter))
        from collective.base.interfaces import IAdapter
        self.assertTrue(issubclass(IShoppingSite, IAdapter))

    def test_instance(self):
        self.assertIsInstance(IShoppingSite(self.portal), ShoppingSite)

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        self.assertTrue(verifyObject(IShoppingSite, IShoppingSite(self.portal)))

    def test_shop(self):
        folder1 = self.create_atcontent('Folder', id='folder1')
        folder2 = self.create_atcontent('Folder', folder1, id='folder2')
        folder3 = self.create_atcontent('Folder', folder2, id='folder3')
        alsoProvides(folder1, IShoppingSiteRoot)
        self.assertIsNone(IShoppingSite(self.portal).shop())
        self.assertEqual(IShoppingSite(folder1).shop(), folder1)
        self.assertEqual(IShoppingSite(folder2).shop(), folder1)
        self.assertEqual(IShoppingSite(folder3).shop(), folder1)

        alsoProvides(folder2, IShoppingSiteRoot)
        self.assertIsNone(IShoppingSite(self.portal).shop())
        self.assertEqual(IShoppingSite(folder1).shop(), folder1)
        self.assertEqual(IShoppingSite(folder2).shop(), folder2)
        self.assertEqual(IShoppingSite(folder3).shop(), folder2)

    def test_shop_path(self):
        folder1 = self.create_atcontent('Folder', id='folder1')
        folder2 = self.create_atcontent('Folder', folder1, id='folder2')
        folder3 = self.create_atcontent('Folder', folder2, id='folder3')
        alsoProvides(folder1, IShoppingSiteRoot)
        self.assertIsNone(IShoppingSite(self.portal).shop_path())
        self.assertEqual(IShoppingSite(folder1).shop_path(), '/plone/folder1')
        self.assertEqual(IShoppingSite(folder2).shop_path(), '/plone/folder1')
        self.assertEqual(IShoppingSite(folder3).shop_path(), '/plone/folder1')

        alsoProvides(folder2, IShoppingSiteRoot)
        self.assertIsNone(IShoppingSite(self.portal).shop_path())
        self.assertEqual(IShoppingSite(folder1).shop_path(), '/plone/folder1')
        self.assertEqual(IShoppingSite(folder2).shop_path(), '/plone/folder1/folder2')
        self.assertEqual(IShoppingSite(folder3).shop_path(), '/plone/folder1/folder2')

    def test_order_container(self):
        self.assertIsNone(IShoppingSite(self.portal).order_container())

        folder = self.create_atcontent('Folder', id='folder')
        self.assertIsNone(IShoppingSite(folder).order_container())

        alsoProvides(folder, IShoppingSiteRoot)
        self.assertIsNone(IShoppingSite(folder).order_container())

        container = self.create_content('collective.cart.core.OrderContainer', folder)
        self.assertEqual(IShoppingSite(folder).order_container(), container)

        noLongerProvides(folder, IShoppingSiteRoot)
        self.assertIsNone(IShoppingSite(folder).order_container())

    def test_cart(self):
        shopping_site = IShoppingSite(self.portal)
        self.assertIsNone(shopping_site.cart())

        session = shopping_site.getSessionData(create=True)
        session.set('collective.cart.core', 'CART')
        self.assertEqual(shopping_site.cart(), 'CART')

    def test_cart_articles(self):
        shopping_site = IShoppingSite(self.portal)
        self.assertIsNone(shopping_site.cart_articles())

        session = shopping_site.getSessionData(create=True)
        session.set('collective.cart.core', {})
        self.assertIsNone(shopping_site.cart_articles())

        session.set('collective.cart.core', {'articles': 'ARTICLES'})
        self.assertEqual(shopping_site.cart_articles(), 'ARTICLES')

    def test_cart_article_listing(self):
        shopping_site = IShoppingSite(self.portal)
        self.assertEqual(shopping_site.cart_article_listing(), [])

        session = shopping_site.getSessionData(create=True)
        session.set('collective.cart.core', {'articles': {'1': 'ARTICLE1', '2': 'ARTICLE2'}})
        self.assertEqual(shopping_site.cart_article_listing(), ['ARTICLE1', 'ARTICLE2'])

    def test_get_cart_article(self):
        shopping_site = IShoppingSite(self.portal)
        self.assertIsNone(shopping_site.get_cart_article('1'))

        session = shopping_site.getSessionData(create=True)
        session.set('collective.cart.core', {'articles': {'1': 'ARTICLE1', '2': 'ARTICLE2'}})

        self.assertIsNone(shopping_site.get_cart_article('3'))
        self.assertEqual(shopping_site.get_cart_article('2'), 'ARTICLE2')

    def test_remove_cart_articles(self):
        shopping_site = IShoppingSite(self.portal)
        session = shopping_site.getSessionData(create=True)
        session.set('collective.cart.core', {'articles': {'1': 'ARTICLE1', '2': 'ARTICLE2', '3': 'ARTICLE3'}})

        self.assertEqual(shopping_site.remove_cart_articles('4'), [])
        self.assertEqual(shopping_site.cart_articles(), {'1': 'ARTICLE1', '2': 'ARTICLE2', '3': 'ARTICLE3'})

        self.assertEqual(shopping_site.remove_cart_articles(['2', '3']), ['ARTICLE2', 'ARTICLE3'])
        self.assertEqual(shopping_site.cart_articles(), {'1': 'ARTICLE1'})

        self.assertEqual(shopping_site.remove_cart_articles('1'), ['ARTICLE1'])
        self.assertEqual(shopping_site.cart_articles(), {})

    def test_update_cart(self):
        adapter = IShoppingSite(self.portal)
        adapter.update_cart('name', 'NAME')
        self.assertIsNone(adapter.getSessionData(create=False))

        session = adapter.getSessionData(create=True)
        session.set('collective.cart.core', {})
        adapter.update_cart('name', 'NAME')
        self.assertEqual(session.get('collective.cart.core'), {'name': 'NAME'})

    def test_remove_from_cart(self):
        adapter = IShoppingSite(self.portal)
        self.assertIsNone(adapter.cart())
        self.assertIsNone(adapter.remove_from_cart('name'))
        self.assertIsNone(adapter.cart())

        session = adapter.getSessionData(create=True)
        session.set('collective.cart.core', {})
        self.assertEqual(adapter.cart(), {})
        self.assertIsNone(adapter.remove_from_cart('name'))
        self.assertEqual(adapter.cart(), {})

        session.set('collective.cart.core', {'name': 'Name'})
        self.assertEqual(adapter.cart(), {'name': 'Name'})
        self.assertEqual(adapter.remove_from_cart('name'), 'Name')
        self.assertEqual(adapter.cart(), {})

    def test_clear_cart(self):
        shopping_site = IShoppingSite(self.portal)
        self.assertIsNone(shopping_site.clear_cart())

        session = shopping_site.getSessionData(create=True)
        session.set('collective.cart.core', {})
        self.assertIsNone(shopping_site.clear_cart())
        self.assertIsNone(session.get('collective.cart.core'))

        session.set('collective.cart.core', {'articles': {'1': 'ARTICLE1'}})
        self.assertIsNone(shopping_site.clear_cart())
        self.assertIsNone(session.get('collective.cart.core'))

    def test_clean_articles_in_cart(self):
        from plone.uuid.interfaces import IUUID
        adapter = IShoppingSite(self.portal)
        self.assertIsNone(adapter.clean_articles_in_cart())

        article1 = self.create_content('collective.cart.core.Article', id='1')
        article2 = self.create_content('collective.cart.core.Article', id='2')
        uuid1 = IUUID(article1)
        uuid2 = IUUID(article2)
        session = adapter.getSessionData(create=True)
        session.set('collective.cart.core', {'articles': {uuid1: 'ARTICLE1', uuid2: 'ARTICLE2'}})
        self.assertEqual(adapter.clean_articles_in_cart(), {uuid1: 'ARTICLE1', uuid2: 'ARTICLE2'})

        self.portal.manage_delObjects(['1', '2'])
        self.assertEqual(adapter.clean_articles_in_cart(), {})

    # CartContainer related methods

    def test_get_order(self):
        adapter = IShoppingSite(self.portal)
        self.assertIsNone(adapter.get_order('1'))

        alsoProvides(self.portal, IShoppingSiteRoot)
        container = self.create_content('collective.cart.core.OrderContainer')
        self.assertIsNone(adapter.get_order('1'))

        order1 = self.create_content('collective.cart.core.Order', container, id='1')
        self.assertIsNone(adapter.get_order('2'))
        self.assertEqual(adapter.get_order('1'), order1)

    @mock.patch('collective.cart.core.adapter.interface.IOrderContainerAdapter')
    def test_update_next_order_id(self, IOrderContainerAdapter):
        alsoProvides(self.portal, IShoppingSiteRoot)
        adapter = IShoppingSite(self.portal)
        adapter.update_next_order_id()
        self.assertFalse(IOrderContainerAdapter.called)

        self.create_content('collective.cart.core.OrderContainer')
        adapter.update_next_order_id()
        self.assertTrue(IOrderContainerAdapter().update_next_order_id.called)

    def test_create_order(self):
        adapter = IShoppingSite(self.portal)
        self.assertIsNone(adapter.create_order())

        order_container = self.create_content('collective.cart.core.OrderContainer')
        adapter.order_container = mock.Mock(return_value=order_container)

        article1 = {
            'id': '1',
            'title': 'Ärticle1',
            'description': 'Description of Ärticle1',
        }
        cart_articles = {'1': article1}
        adapter.cart_articles = mock.Mock(return_value=cart_articles)

        adapter.update_next_order_id = mock.Mock()
        order1 = adapter.create_order()
        self.assertEqual(order1.id, '1')

        order_article1 = order1['1']
        self.assertEqual(order_article1.title, article1['title'])
        self.assertEqual(order_article1.description, article1['description'])

        order3 = adapter.create_order('3')
        self.assertEqual(order3.id, '3')
