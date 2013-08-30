# -*- coding: utf-8 -*-
from zope import interface, schema
from plone.theme.interfaces import IDefaultPloneLayer
from collective.liches import lichesMessageFactory as _

class ILichesLayer(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.
    """

class ILichesSettingsSchema(interface.Interface):

    content_types = schema.List(
        title = _(u'Content types'),
        required = False,
        default = [u'Link', u'Event', u'Document', u'News Item'],
        description = _(u"A list of types to be checked",),
        value_type = schema.Choice(title=_(u"Content types"),
            source="plone.app.vocabularies.ReallyUserFriendlyTypes")
        )

    liches_server = schema.TextLine(
        title = _(u'Liches Server'),
        description = _(u'Adress of the liches server'),
        required = True,
        default = u'http://localhost:6543',
    )

    secret_key = schema.TextLine(
        title = _(u'Secret Key'),
        description = _(u'Key to authenticate to the liches server'),
        required = True,
    )

    invalid_only = schema.Bool(
        title = _(u"Invalid only"),
        description = _("Do not show valid links with warnings"),
        required = False,
        default = True,
    )
