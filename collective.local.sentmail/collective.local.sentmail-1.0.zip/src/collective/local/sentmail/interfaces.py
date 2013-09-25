# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""
from zope import schema

from plone.app.textfield import RichText
from plone.supermodel import model
from plone.theme.interfaces import IDefaultPloneLayer

from . import _


class ICollectiveLocalSentmailLayer(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer."""


class ISentMail(model.Schema):
    """Schema for sent mail"""

    recipients = schema.List(title=_(u"Recipients"),
                             value_type=schema.Choice(vocabulary='plone.principalsource.Principals'))

    body = RichText(title=_(u"Body text"),
                    default_mime_type='text/html',
                    output_mime_type="text/x-html-safe",
                    )
