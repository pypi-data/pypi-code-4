# -*- encoding: utf-8 -*-

from Products.CMFCore.utils import getToolByName
from plone.app.registry.browser import controlpanel
from plone.registry.interfaces import IRecordModifiedEvent
from zope.component.hooks import getSite
from zope import component
from collective.addthis.interfaces import IAddThisSettings
from collective.addthis import _


class AddThisSettingsForm(controlpanel.RegistryEditForm):
    schema = IAddThisSettings
    id = "addthis-settings"
    label = _(u"AddThis settings")
    description = _(u"Set your own AddThis URL and social media chicklets "
                     "by using this form")

    def updateFields(self):
        super(AddThisSettingsForm, self).updateFields()

    def updateWidgets(self):
        super(AddThisSettingsForm, self).updateWidgets()

    def update(self):
        super(AddThisSettingsForm, self).update()
        #update social media sources
        updater = component.getMultiAdapter((self.context, self.request),
                                  name=u'addthis-social-media-updater')
        updater()


class AddThisControlPanel(controlpanel.ControlPanelFormWrapper):
    form = AddThisSettingsForm


def notify_configuration_changed(event):
    """
    Event subscriber that is called when configuration has changed.
    """

    portal = getSite()
    js_registry = getToolByName(portal, 'portal_javascripts', None)

    if IRecordModifiedEvent.providedBy(event):
        # AddThis control panel setting changed
        if event.record.fieldName == 'addthis_load_asynchronously':
            jsid = '++resource++collective.addthis/addthis.js'
            if event.record.value == True:
                # Enable asynchronous loading
                js = js_registry.getResource(jsid)
                if not js.getEnabled():
                    js.setEnabled(True)
            else:
                # Disable asynchronous loading
                js = js_registry.getResource(jsid)
                if js.getEnabled():
                    js.setEnabled(False)

                js_registry
