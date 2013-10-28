# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from collective.cart.core.adapter.article import ArticleAdapter
from collective.cart.core.interfaces import IArticleAdapter
from collective.cart.core.tests.base import IntegrationTestCase

import mock


class TestArticleAdapter(IntegrationTestCase):
    """TestCase for ArticleAdapter"""

    def test_subclass(self):
        from collective.base.adapter import Adapter
        self.assertTrue(issubclass(ArticleAdapter, Adapter))
        from collective.base.interfaces import IAdapter
        self.assertTrue(issubclass(IArticleAdapter, IAdapter))

    def test_instance(self):
        article = self.create_content('collective.cart.core.Article')
        self.assertIsInstance(IArticleAdapter(article), ArticleAdapter)

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        article = self.create_content('collective.cart.core.Article')
        self.assertTrue(verifyObject(IArticleAdapter, IArticleAdapter(article)))

    def test_addable_to_cart(self):
        article = self.create_content('collective.cart.core.Article')
        self.assertTrue(IArticleAdapter(article).addable_to_cart())

        article.salable = False
        self.assertFalse(IArticleAdapter(article).addable_to_cart())

        article.salable = True
        self.assertTrue(IArticleAdapter(article).addable_to_cart())

    def test_add_to_cart(self):
        from plone.uuid.interfaces import IUUID
        session_data_manager = getToolByName(self.portal, 'session_data_manager')
        session = session_data_manager.getSessionData(create=False)
        self.assertIsNone(session)

        article1 = self.create_content('collective.cart.core.Article', id='1', title='Ärticle1', description='Descriptiön of Ärticle1')
        uuid1 = IUUID(article1)
        article2 = self.create_content('collective.cart.core.Article', id='2', title='Ärticle2', description='Descriptiön of Ärticle2')
        uuid2 = IUUID(article2)
        adapter = IArticleAdapter(article1)
        adapter._update_existing_cart_article = mock.Mock()
        adapter.add_to_cart()
        session = session_data_manager.getSessionData(create=False)
        self.assertEqual(len(session.get('collective.cart.core').get('articles')), 1)
        self.assertEqual(sorted(session.get('collective.cart.core').get('articles').get(uuid1).items()),
            [
                ('description', 'Descriptiön of Ärticle1'),
                ('id', uuid1),
                ('title', 'Ärticle1'),
                ('url', 'http://nohost/plone/article1')])
        self.assertFalse(adapter._update_existing_cart_article.called)

        adapter.add_to_cart()
        self.assertEqual(len(session.get('collective.cart.core').get('articles')), 1)
        self.assertEqual(sorted(session.get('collective.cart.core').get('articles').get(uuid1).items()),
            [
                ('description', 'Descriptiön of Ärticle1'),
                ('id', uuid1),
                ('title', 'Ärticle1'),
                ('url', 'http://nohost/plone/article1')])
        self.assertTrue(adapter._update_existing_cart_article.called)

        adapter = IArticleAdapter(article2)
        adapter.add_to_cart()
        self.assertEqual(len(session.get('collective.cart.core').get('articles')), 2)
        self.assertEqual(sorted(session.get('collective.cart.core').get('articles').get(uuid1).items()),
            [
                ('description', 'Descriptiön of Ärticle1'),
                ('id', uuid1),
                ('title', 'Ärticle1'),
                ('url', 'http://nohost/plone/article1')])
        self.assertEqual(sorted(session.get('collective.cart.core').get('articles').get(uuid2).items()),
            [
                ('description', 'Descriptiön of Ärticle2'),
                ('id', uuid2),
                ('title', 'Ärticle2'),
                ('url', 'http://nohost/plone/article2')])
