from collective.cart.core.adapter.order import OrderAdapter
from collective.cart.core.interfaces import IOrderAdapter
from collective.cart.core.tests.base import IntegrationTestCase


class OrderAdapterTestCasae(IntegrationTestCase):
    """TestCase for OrderAdapter"""

    def test_subclass(self):
        from collective.base.adapter import Adapter
        self.assertTrue(issubclass(OrderAdapter, Adapter))
        from collective.base.interfaces import IAdapter
        self.assertTrue(issubclass(IOrderAdapter, IAdapter))

    def test_instance(self):
        order = self.create_content('collective.cart.core.Order')
        self.assertIsInstance(IOrderAdapter(order), OrderAdapter)

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        order = self.create_content('collective.cart.core.Order')
        self.assertTrue(verifyObject(IOrderAdapter, IOrderAdapter(order)))

    def test_articles(self):
        order = self.create_content('collective.cart.core.Order', id='1')
        adapter = IOrderAdapter(order)
        self.assertEqual(len(adapter.articles()), 0)

        self.create_content('collective.cart.core.OrderArticle', order, id='1')
        self.create_content('collective.cart.core.OrderArticle', order, id='2')
        self.assertEqual(len(adapter.articles()), 2)

    def test_get_article(self):
        order = self.create_content('collective.cart.core.Order', id='1')
        adapter = IOrderAdapter(order)
        self.assertIsNone(adapter.get_article('1'))

        article1 = self.create_content('collective.cart.core.OrderArticle', order, id='1')
        self.assertIsNone(adapter.get_article('2'))
        self.assertEqual(adapter.get_article('1'), article1)
