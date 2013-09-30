from plone.app.registry.browser import controlpanel
from pcommerce.payment.docdata import MessageFactory as _
from interfaces import IDocdataSettings


class DocdataSettingsEditForm(controlpanel.RegistryEditForm):

    schema = IDocdataSettings
    label = _(u"Docdata PCommerce settings")
    description = _(u"The Docdata settings for PCommerce")

    def updateFields(self):
        super(DocdataSettingsEditForm, self).updateFields()

    def updateWidgets(self):
        super(DocdataSettingsEditForm, self).updateWidgets()


class DocdataSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = DocdataSettingsEditForm
