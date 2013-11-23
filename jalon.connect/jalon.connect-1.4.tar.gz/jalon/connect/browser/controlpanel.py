# -*- coding: utf-8 -*-

from zope.interface import implements
from zope.i18nmessageid import MessageFactory
from plone.fieldsets.fieldsets import FormFieldsets
from plone.app.controlpanel.form import ControlPanelForm

from jalon.connect import contentMessageFactory as _
from jalon.connect.interfaces.utility import IConnectLayout, IConnectModele
from jalon.connect.browser.interfaces.controlpanel import IConnectControlPanelForm

class ConnectControlPanelForm(ControlPanelForm):
    """Connect Control Panel Form"""
    implements(IConnectControlPanelForm)

    connectlayout = FormFieldsets(IConnectLayout)
    connectlayout.id = 'connectlayout'
    connectlayout.label = _(u'Connexion')

    connectmodele = FormFieldsets(IConnectModele)
    connectmodele.id = 'connectmodele'
    connectmodele.label = _(u'Modèle')

    form_fields = FormFieldsets(connectlayout, connectmodele) # Connectlibraries

    label = _(u"Connect Settings")
    description = _(u"Settings for the Connect connector.")
    form_name = _("Connect Settings")
