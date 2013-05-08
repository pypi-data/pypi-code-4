#-*- coding: utf-8 -*-
from plone.app.registry.browser import controlpanel
from ityou.whoisonline.interfaces import IWhoIsOnlineSettings, _

class WhoIsOnlineSettingsEditForm(controlpanel.RegistryEditForm):

    schema = IWhoIsOnlineSettings
    label = _(u"Who is online settings")
    description = _(u"""Settings of the 'who is online' variables
    """)

    def updateFields(self):
        super(WhoIsOnlineSettingsEditForm, self).updateFields()

    def updateWidgets(self):
        super(WhoIsOnlineSettingsEditForm, self).updateWidgets()

class WhoIsOnlineSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = WhoIsOnlineSettingsEditForm
