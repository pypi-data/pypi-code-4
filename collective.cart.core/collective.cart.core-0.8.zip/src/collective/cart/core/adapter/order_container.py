from collective.base.adapter import Adapter
from collective.cart.core.interfaces import IOrderContainer
from collective.cart.core.interfaces import IOrderContainerAdapter
from zope.component import adapts
from zope.interface import implements


class OrderContainerAdapter(Adapter):
    """Adapter for content type: collective.cartr.core.OrderContainer."""

    adapts(IOrderContainer)
    implements(IOrderContainerAdapter)

    def update_next_order_id(self):
        """Update next_order_id"""
        cid = self.context.next_order_id
        while str(cid) in self.context.objectIds():
            cid += 1
        self.context.next_order_id = cid
