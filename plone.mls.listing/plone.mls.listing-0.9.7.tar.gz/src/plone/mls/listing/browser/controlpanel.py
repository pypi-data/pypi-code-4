# -*- coding: utf-8 -*-
"""MLS Agency Contact Info Settings Control Panel."""

# zope imports
from plone.app.registry.browser import controlpanel

# local imports
# from plone.mls.listing.i18n import _
from plone.mls.listing.interfaces import IMLSAgencyContactInformation


class MLSAgencyContactInfoSettingsEditForm(controlpanel.RegistryEditForm):
    """MLS Agency Contact Info Settings Form."""

    schema = IMLSAgencyContactInformation
    label = u''

    def updateFields(self):
        super(MLSAgencyContactInfoSettingsEditForm, self).updateFields()

    def updateWidgets(self):
        super(MLSAgencyContactInfoSettingsEditForm, self).updateWidgets()


class MLSAgencyContactInfoSettingsControlPanel(
        controlpanel.ControlPanelFormWrapper):
    """MLS Agency Contact Info Settings Control Panel."""

    form = MLSAgencyContactInfoSettingsEditForm
