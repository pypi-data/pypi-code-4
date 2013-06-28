from plone.supermodel import model
from zope import schema
from collective.readitlater.i18n import _


class IUrl(model.Schema):
    """Interface for content type storing a URL"""
    url = schema.ASCIILine(title=_(u"URL"))
    title = schema.TextLine(title=_(u"Title"))
    description = schema.Text(
        title=_(u"Description"),
        required=False
    )
