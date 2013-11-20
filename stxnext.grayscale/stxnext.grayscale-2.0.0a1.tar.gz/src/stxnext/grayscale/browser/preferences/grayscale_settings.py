# -*- coding:utf-8 -*-
import os
import shutil

from Products.CMFDefault.formlib.schema import ProxyFieldProperty
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.statusmessages.interfaces import IStatusMessage
from plone.app.controlpanel.events import ConfigurationChangedEvent
from plone.app.controlpanel.form import ControlPanelForm
from plone.app.controlpanel.site import SiteControlPanelAdapter
from plone.protect import CheckAuthenticator
from zope.component import adapts
from zope.component.hooks import getSite
from zope.event import notify
from zope.interface import Interface, implements
from zope.formlib.form import action, applyChanges, FormFields
from zope.schema import Bool, Choice, Tuple

from stxnext.grayscale import log
from stxnext.grayscale import StxnextGrayscaleMessageFactory as _
from stxnext.grayscale.config import TYPE, THEME


class IGrayscaleSettingsSchema(Interface):
    """
    Interface for additional control panel settings
    """

    transformed_themes = Tuple(
        title = _(u'Skins transformed to grayscale'),
        description = _(u'Select skin to be transformed to grayscale'),
        required = False,
        value_type = Choice(required = False,
            vocabulary = 'plone.app.vocabularies.Skins')
    )

    delete_cached_resources = Bool(
        title = _(u'Delete cached resources'),
        description=_(u'Select the checkbox to delete the gray-scale ' \
                      u'converted resources from the filesystem cache.'),
    )


class GrayscaleControlPanelAdapter(SiteControlPanelAdapter):
    """
    Storage for grayscale site control panel settings
    """

    adapts(IPloneSiteRoot)
    implements(IGrayscaleSettingsSchema)

    transformed_themes = ProxyFieldProperty(IGrayscaleSettingsSchema[
        'transformed_themes'
    ])
    delete_cached_resources = False


class GrayscaleSettingsForm(ControlPanelForm):
    """
    Grayscale transformation skins settings form
    """

    form_fields = FormFields(IGrayscaleSettingsSchema)

    label = _('Grayscale settings')
    description = ''
    form_name = _('Grayscale skin settings')

    def setUpWidgets(self, ignore_request=False):
        """
        Disabling the widget for removing filestorage cache in case of
        lack of grayscale resources dir registered
        """
        super(GrayscaleSettingsForm, self).setUpWidgets(ignore_request=ignore_request)
        dcr_widget = self.widgets['delete_cached_resources']
        site = getSite()
        path = str('/++%s++%s' % (TYPE, THEME))
        try:
            location = site.restrictedTraverse(path)
        except AttributeError:
            dcr_widget.disabled = True

    @action(_(u'label_save', default=u'Save'), name=u'save')
    def handle_edit_action(self, action, data):
        CheckAuthenticator(self.request)
        if applyChanges(self.context, self.form_fields, data, self.adapters):
            notify(ConfigurationChangedEvent(self, data))
            return self._on_save(data)

    def _on_save(self, data):
        """
        Deleting the gray-scale converted resources
        from the filesystem cache
        """
        messages = IStatusMessage(self.request)
        if data.get('delete_cached_resources'):
            site = getSite()
            try:
                path = str('/++%s++%s' % (TYPE, THEME))
                location = site.restrictedTraverse(path).directory
            except AttributeError, e:
                log.info('Unable to remove files for: %s due to error: %s' % (path, e))
                message = _(u"Couldn't remove files from %s" % path)
                messages.addStatusMessage(message, type='error')
                return

            try:
                log.info('Removing cached gray-scale files from: %s' % location)
                for filename in os.listdir(location):
                    file_path = os.path.join(location, filename)
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                    else:
                        shutil.rmtree(file_path)
            except OSError, e:
                log.info('Unable to remove files from: %s, error: %s' % (location, e))
                message = _(u"Couldn't remove files from %s" % location)
                messages.addStatusMessage(message, type='error')
            else:
                message = _(u'Files from path %s have been removed.' % location)
                messages.addStatusMessage(message, type='info')
