from collective.base.adapter import Adapter
from collective.cart.core.interfaces import IOrder
from collective.cart.core.interfaces import IOrderAdapter
from collective.cart.core.interfaces import IOrderArticle
from zope.component import adapts
from zope.interface import implements


class OrderAdapter(Adapter):
    """Adapter for content type: collective.cart.core.Order"""

    adapts(IOrder)
    implements(IOrderAdapter)

    def articles(self):
        """Returns list of brains of OrderArticle"""
        return self.get_brains(IOrderArticle, depth=1)

    def get_article(self, oid):
        """Returns CartArticle form order by ID"""
        return self.get_object(IOrderArticle, depth=1, id=oid)
