from plone.app.portlets.interfaces import IColumn
from zope import schema
from zope.interface import Interface


class IFooterSettings(Interface):

    columns_count = schema.Choice(title=u"Footer Columns count",
                                  description=u"Defines how many Columns \
                                  there are in the Footer",
                                  values=[1, 2, 4],
                                  default=4
                                  )


class IFtwFooterLayer(Interface):
    """Request marker interface"""


class IFooterColumn(IColumn):
    """Footer columns"""
