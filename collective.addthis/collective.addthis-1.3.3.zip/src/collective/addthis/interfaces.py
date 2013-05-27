# -*- coding: utf-8 -*-

from zope.interface import Interface
from zope import schema
from collective.addthis import _
from plone.theme.interfaces import IDefaultPloneLayer


class IAddThis(Interface):
    """ AddThis marker """


class IAddThisBrowserLayer(IDefaultPloneLayer):
    """AddThis marker"""


class IAddthisBrowserLayer(IDefaultPloneLayer):
    """Old Addthis marker"""


class IAddThisSettings(Interface):
    """
    AddThis control panel settings used to effect the rendering of the
    addthis viewlet.
    """

    addthis_activated = schema.Bool(
        title=_(u"Activate AddThis"),
        default=True,)

    addthis_account_name = schema.TextLine(
        title=_(u"AddThis account name"),
        default=u"",
        required=False,)

    addthis_url = schema.URI(
        title=_(u"AddThis URL"),
        description=_(u"AddThis bookmark URL. Usually there is no need to "
                      "change this."),
        required=False,
        default="http://www.addthis.com/bookmark.php?v=250")

    addthis_script_url = schema.URI(
        title=_(u"AddThis JavaScript URL"),
        description=_(u"URL to AddThis javascript. Usually there is no "
                      "reason to change this."),
        required=False,
        default="http://s7.addthis.com/js/250/addthis_widget.js")

    addthis_chicklets = schema.List(
        title=_(u"Social media selection"),
        description=_(u"A list of social media items that will be displayed "
                       "along side the share link as individual chicklets."),
        required=False,
        default=[],
        value_type=schema.Choice(title=_(u"Social media"),
                                 vocabulary="AddThis Social Media"),
        )

    addthis_load_asynchronously = schema.Bool(
        title=_(u"Load AddThis resources asynchronously"),
        description=_(u"By enabling this AddThis loads it's resources only "
                      "after whole page has been fully loaded. This prevents "
                      "AddThis from blocking page load."),
        default=False,)

    addthis_data_track_addressbar = schema.Bool(
        title=_(u"Address Bar Sharing"),
        description=_(u"(Beta). Measures when users copy your URL from their"
                       " browser. Add an analytics fragment to the URL."),
        default=False,)

    addthis_data_track_clickback = schema.Bool(
        title=_(u"Add clickback tracking variable to URL"),
        description=_(u"Use this to track how many people come back to your "
                       "content via links shared with AddThis."),
        default=False,)

    addthis_button_visible = schema.Bool(
        title=_(u"Show AddThis button before social media items."),
        default=True,)


class ISocialMedia(Interface):
    """A source of listing of social media supported by the addthis service."""

    sources = schema.Iterable(
        title=_(u"Social media sources"),
        description=_(u"A list of valid social media."),
        )
