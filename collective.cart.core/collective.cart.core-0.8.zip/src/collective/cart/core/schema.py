from collective.cart.core import _
from plone.supermodel.model import Schema
from zope import schema


class ArticleSchema(Schema):
    """Schema for content type: collective.cart.core.Article"""


class OrderContainerSchema(Schema):
    """Schema for content type: collective.cart.core.OrderContainer"""

    next_order_id = schema.Int(
        title=_(u'Next Order ID'),
        default=1,
        min=1)


class OrderSchema(Schema):
    """Schema for content type: collective.cart.core.Order"""

    description = schema.Text(
        title=_(u'Description'),
        required=False)


class OrderArticleSchema(Schema):
    """Schema for content type: collective.cart.core.OrderArticle"""
