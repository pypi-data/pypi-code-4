import json
from plone.app.registry.browser import controlpanel
from z3c.form import interfaces
from zope import interface
from zope import schema

from collective.readitlater.i18n import _


class IReaditlaterSettings(interface.Interface):
    """Global configuration fo collective.readitlater add-on."""

    folder_query = schema.ASCII(
        title=_(u"Folder query"),
        description=_(u"help_readitlater_folder_query",
                      default=u"Query used to search for folder the user can add urls in. In JSON."),
    )

    @interface.invariant
    def _folder_query_is_json(obj):
        try:
            json.loads(obj.folder_query)
        except ValueError:
            raise interface.Invalid("Not a valid JSON.")


class ReaditlaterSettingsEditForm(controlpanel.RegistryEditForm):
    schema = IReaditlaterSettings
    label = _(u"collective.readitlater settings")

    def updateFields(self):
        super(ReaditlaterSettingsEditForm, self).updateFields()

    def updateWidgets(self):
        super(ReaditlaterSettingsEditForm, self).updateWidgets()


class ReaditlaterSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = ReaditlaterSettingsEditForm
