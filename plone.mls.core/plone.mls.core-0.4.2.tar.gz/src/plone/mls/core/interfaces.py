# -*- coding: utf-8 -*-
"""Interface definitions."""

# zope imports
from zope import schema
from zope.interface import Interface

# local imports
from plone.mls.core.i18n import _


class IMLSSettings(Interface):
    """Global Propertyshelf MLS settings.

    This describes records stored in the configuration registry and obtainable
    via plone.registry.
    """

    mls_key = schema.TextLine(
        default=u"",
        required=False,
        title=_(
            u"label_mls_key",
            default=u"MLS API Key",
        )
    )

    mls_site = schema.TextLine(
        default=u"",
        required=True,
        title=_(
            u"label_mls_site",
            default=u"MLS URL",
        )
    )

    agency_id = schema.TextLine(
        default=u"",
        required=True,
        title=_(
            u"label_agency_id",
            default=u"Agency ID",
        )
    )
