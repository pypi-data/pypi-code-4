from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from hexagonit.socialbutton import _
from hexagonit.socialbutton.data import SocialButtonCode
from hexagonit.socialbutton.data import SocialButtonConfig
from hexagonit.socialbutton.interfaces import IAddSocialButtonCode
from hexagonit.socialbutton.interfaces import IAddSocialButtonConfig
from hexagonit.socialbutton.interfaces import ISocialButtonCode
from hexagonit.socialbutton.interfaces import ISocialButtonConfig
from hexagonit.socialbutton.utility import IConvertToUnicode
from plone.registry.interfaces import IRegistry
from plone.z3cform.crud import crud
from zope.component import getUtility


class BaseCrudForm(crud.CrudForm):
    """Base Crud Form"""

    def add(self, data):
        """Add new data to registry.

        :param data: data.
        :type data: dict
        """
        data = getUtility(IConvertToUnicode)(data)
        registry = getUtility(IRegistry)
        items = registry[self._record_name] or {}
        items[data.pop('code_id')] = data
        registry[self._record_name] = items

    def get_items(self):
        """Get items to show on the form."""
        registry = getUtility(IRegistry)
        items = registry[self._record_name]
        data = []
        for key in items:
            code_id = str(key)
            instance = self._class(code_id, **items[key])
            data.append((code_id, instance))
        return data

    def remove(self, (code_id, item)):
        """Delete data from registry.

        :param code_id: ID for social button.
        :type code_id: unicode

        :param item: item instance.
        :type item: obj
        """
        registry = getUtility(IRegistry)
        items = registry[self._record_name]
        del items[code_id]
        registry[self._record_name] = items

    def before_update(self, item, data):
        """Update field values.

        :param item: data instance.
        :type item: object

        :param data: Field key and value.
        :type data: dict
        """
        registry = getUtility(IRegistry)
        items = registry[self._record_name]
        data = getUtility(IConvertToUnicode)(data)
        items[item.code_id] = data
        registry[self._record_name] = items


class SocialButtonCodeForm(BaseCrudForm):
    """Form for updating social button code at ControlPanel."""
    label = _(u'Social Button Code Setting')
    update_schema = ISocialButtonCode
    _record_name = 'hexagonit.socialbutton.codes'
    _class = SocialButtonCode

    @property
    def add_schema(self):
        return IAddSocialButtonCode

    def update(self):
        super(self.__class__, self).update()
        edit_forms = self.subforms[0]
        forms = edit_forms.subforms
        cols = 70
        for form in forms:
            code_text_widget = form.widgets['code_text']
            code_text_widget.cols = cols
        add_form = self.subforms[1]
        add_form.widgets['code_text'].cols = cols


class SocialButtonConfigForm(BaseCrudForm):
    """Form for updating social button configuration at ControlPanel."""

    label = _(u'Social Button Configuration')
    update_schema = ISocialButtonConfig
    _record_name = 'hexagonit.socialbutton.config'
    _class = SocialButtonConfig

    @property
    def add_schema(self):
        return IAddSocialButtonConfig


class BaseControlPanelView(BrowserView):
    __call__ = ViewPageTemplateFile('templates/controlpanel.pt')


class SocialButtonCodeControlPanelView(BaseControlPanelView):

    def form(self):
        return SocialButtonCodeForm(self.context, self.request)()


class SocialButtonConfigControlPanelView(BaseControlPanelView):

    def form(self):
        return SocialButtonConfigForm(self.context, self.request)()
