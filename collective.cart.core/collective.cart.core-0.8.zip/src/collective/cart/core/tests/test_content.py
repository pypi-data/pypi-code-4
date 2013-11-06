from collective.cart.core.content import Article
from collective.cart.core.content import Order
from collective.cart.core.content import OrderArticle
from collective.cart.core.content import OrderContainer
from collective.cart.core.interfaces import IArticle
from collective.cart.core.interfaces import IOrder
from collective.cart.core.interfaces import IOrderArticle
from collective.cart.core.interfaces import IOrderContainer
from plone.dexterity.content import Container
from plone.dexterity.interfaces import IDexterityContainer
from zope.interface.verify import verifyObject

import unittest


class ArticleTestCase(unittest.TestCase):
    """TestCase for content type: collective.cart.core.Article"""

    def test_subclass(self):
        from collective.cart.core.schema import ArticleSchema
        self.assertTrue(issubclass(Article, Container))
        self.assertTrue(issubclass(IArticle, (ArticleSchema, IDexterityContainer)))

    def test_instance__verifyObject(self):
        self.assertTrue(verifyObject(IArticle, Article()))


class OrderContainerTestCase(unittest.TestCase):
    """TestCase for content type: collective.cart.core.OrderContainer"""

    def test_subclass(self):
        from collective.cart.core.schema import OrderContainerSchema
        self.assertTrue(issubclass(OrderContainer, Container))
        self.assertTrue(issubclass(IOrderContainer, (OrderContainerSchema, IDexterityContainer)))

    def test_instance__verifyObject(self):
        self.assertTrue(verifyObject(IOrderContainer, OrderContainer()))


class OrderTestCase(unittest.TestCase):
    """TestCase for content type: collective.cart.core.Order"""

    def test_subclass(self):
        from collective.cart.core.schema import OrderSchema
        self.assertTrue(issubclass(Order, Container))
        self.assertTrue(issubclass(IOrder, (OrderSchema, IDexterityContainer)))

    def test_instance__verifyObject(self):
        self.assertTrue(verifyObject(IOrder, Order()))


class OrderArticleTestCase(unittest.TestCase):
    """TestCase for content type: collective.cart.core.OrderArticle"""

    def test_subclass(self):
        from collective.cart.core.schema import OrderArticleSchema
        self.assertTrue(issubclass(OrderArticle, Container))
        self.assertTrue(issubclass(IOrderArticle, (OrderArticleSchema, IDexterityContainer)))

    def test_instance__verifyObject(self):
        self.assertTrue(verifyObject(IOrderArticle, OrderArticle()))
