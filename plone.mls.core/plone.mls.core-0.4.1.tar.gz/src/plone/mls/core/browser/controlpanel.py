# -*- coding: utf-8 -*-
"""MLS Settings Control Panel."""

# zope imports
from plone.app.registry.browser import controlpanel

# local imports
from plone.mls.core.i18n import _
from plone.mls.core.interfaces import IMLSSettings


class MLSSettingsEditForm(controlpanel.RegistryEditForm):
    """MLS Settings Form"""

    schema = IMLSSettings
    label = _(u"heading_mls_settings", u"Propertyshelf MLS Settings")

    def updateFields(self):
        super(MLSSettingsEditForm, self).updateFields()

    def updateWidgets(self):
        super(MLSSettingsEditForm, self).updateWidgets()


class MLSSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    """MLS Settings Control Panel"""

    form = MLSSettingsEditForm
