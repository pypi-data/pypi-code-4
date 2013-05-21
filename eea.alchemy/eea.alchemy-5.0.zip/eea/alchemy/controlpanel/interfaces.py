""" Interfaces
"""
from zope.interface import Interface
from zope import schema
from eea.alchemy.config import EEAMessageFactory as _

class IAlchemySettings(Interface):
    """ Alchemy settings
    """
    token = schema.TextLine(
        title=_(u"Token"),
        description=_(u"Provide token from "
                      "http://www.alchemyapi.com/api/register.html"),
        required=True,
        default=u""
    )

    autoTagging = schema.Bool(
        title=_(u'Enable auto tagging'),
        description=_(u"Hyperlink tags within page's body"),
        required=False,
        default=False
    )

    autoTaggingFields = schema.List(
        title=_(u"Tagging fields"),
        description=_(u"Lookup these fields for tags"),
        required=True,
        default=[u"subject"],
        value_type=schema.TextLine()
    )

    autoTaggingLink = schema.TextLine(
        title=_(u"Tagging link"),
        description=_(u"Hyperlink to the following address"),
        required=True,
        default=u"@@search?Subject="
    )

    autoTaggingBlackList = schema.List(
        title=_(u'Tagging blacklist'),
        description=_(u"Do not apply auto-tagging if the tag is a child of the "
                      "following HTML elements. "
                      "(use CSS selectors like: div.documentByLine) "
                      "By default auto-tagging will not be applied on text "
                      "that is already a child of an <a> HTML tag"),
        required=False,
        default=[u"h1", u"h2", u"h3"],
        value_type=schema.TextLine()
    )
