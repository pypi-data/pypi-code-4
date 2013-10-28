from collective.cart.core.interfaces import IArticle
from collective.cart.core.interfaces import IOrder
from collective.cart.core.interfaces import IOrderArticle
from collective.cart.core.interfaces import IOrderContainer
from plone.dexterity.content import Container
from zope.interface import implements


class Article(Container):
    """Content type: collective.cart.core.Article"""
    implements(IArticle)


class OrderContainer(Container):
    """Content type: collective.cart.core.OrderContainer"""
    implements(IOrderContainer)

    next_order_id = 1


class Order(Container):
    """Content type: collective.cart.core.Order"""
    implements(IOrder)


class OrderArticle(Container):
    """Content type: collective.cart.core.OrderArticle

    We set original article uuid as id here.
    """
    implements(IOrderArticle)
