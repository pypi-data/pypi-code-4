# -*- coding: utf-8 -*-
from z3c.form import button

from plone.app.registry.browser import controlpanel
from Products.statusmessages.interfaces import IStatusMessage

from collective.liches import lichesMessageFactory as _
from collective.liches.interfaces import ILichesSettingsSchema

class LichesSettings(controlpanel.RegistryEditForm):
    schema = ILichesSettingsSchema
    label = _(u'Liches Settings')
    description = _(u'Configure the access to you Link CHecher Server')

    @button.buttonAndHandler(_('Save'), name='save')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        changes = self.applyChanges(data)
        IStatusMessage(self.request).addStatusMessage(_(u"Changes saved"), "info")
        self.request.response.redirect("%s/%s" % (self.context.absolute_url(), self.control_panel_view))

    @button.buttonAndHandler(_('Cancel'), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(_(u"Edit cancelled"), "info")
        self.request.response.redirect("%s/%s" % (self.context.absolute_url(), self.control_panel_view))

    @button.buttonAndHandler(_('Startpage'), name='startpage')
    def actionStartpage(self, action):
        next_url = self.context.absolute_url() + '/@@linkchecker-startpage.html'
        self.request.response.redirect(next_url)

    @button.buttonAndHandler(_('Broken Pages'), name='brokenpages')
    def actionBrokenPages(self, action):
        next_url = self.context.absolute_url() + '/@@linkchecker-brokenpages.html'
        self.request.response.redirect(next_url)

class LichesSettingsSchemaControlPanel(controlpanel.ControlPanelFormWrapper):
    form = LichesSettings
