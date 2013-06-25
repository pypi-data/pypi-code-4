#-*- coding: utf-8 -*-

from plone.app.registry.browser import controlpanel

from ityou.astream.interfaces import IAstreamSettings, _

class AstreamSettingsEditForm(controlpanel.RegistryEditForm):

    schema = IAstreamSettings
    label = _(u"Activity Stream settings")
    description = _(u"""Settings of the activity stream variables
    """)

    def updateFields(self):
        super(AstreamSettingsEditForm, self).updateFields()


    def updateWidgets(self):
        super(AstreamSettingsEditForm, self).updateWidgets()

class AstreamSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = AstreamSettingsEditForm