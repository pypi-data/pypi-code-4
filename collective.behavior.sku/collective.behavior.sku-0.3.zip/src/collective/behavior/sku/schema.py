from collective.behavior.sku import _
from plone.supermodel.model import Schema
from zope import schema


class SKUSchema(Schema):
    """Schema for behavior: SKU"""

    sku = schema.TextLine(
        title=_(u"SKU"),
        description=_(u"Unique ID for Stock Keeping Unit."))
