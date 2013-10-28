from collective.cart.core.adapter.order_container import OrderContainerAdapter
from collective.cart.core.interfaces import IOrderContainerAdapter
from collective.cart.core.tests.base import IntegrationTestCase


class OrderContainerAdapterTestCase(IntegrationTestCase):
    """TestCase for OrderContainerAdapter"""

    def test_subclass(self):
        from collective.base.adapter import Adapter
        self.assertTrue(issubclass(OrderContainerAdapter, Adapter))
        from collective.base.interfaces import IAdapter
        self.assertTrue(issubclass(IOrderContainerAdapter, IAdapter))

    def test_instance(self):
        container = self.create_content('collective.cart.core.OrderContainer')
        self.assertIsInstance(IOrderContainerAdapter(container), OrderContainerAdapter)

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        container = self.create_content('collective.cart.core.OrderContainer')
        self.assertTrue(verifyObject(IOrderContainerAdapter, IOrderContainerAdapter(container)))

    def test_update_next_order_id(self):
        container = self.create_content('collective.cart.core.OrderContainer')
        adapter = IOrderContainerAdapter(container)
        adapter.update_next_order_id()
        self.assertEqual(container.next_order_id, 1)

        # Add order with ID: 1
        self.create_content('collective.cart.core.Order', container, id="1")
        adapter.update_next_order_id()
        self.assertEqual(container.next_order_id, 2)

        # Add carts with ID: 2 and 3
        self.create_content('collective.cart.core.Order', container, id="2")
        self.create_content('collective.cart.core.Order', container, id="3")
        adapter.update_next_order_id()
        self.assertEqual(container.next_order_id, 4)
