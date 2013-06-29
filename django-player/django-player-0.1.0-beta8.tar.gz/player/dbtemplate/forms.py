from django import forms
from django.conf import settings
from django.template import TemplateDoesNotExist
from django.template.loader import find_template_loader
from django.utils.translation import ugettext_lazy as _

from dbtemplates.admin import TemplateAdminForm as BaseTemplateForm, TemplateContentTextArea
from dbtemplates.models import Template

from player.base.forms import BaseForm


class TemplateAdminForm(BaseForm, BaseTemplateForm):
    content = forms.CharField(
        widget=TemplateContentTextArea({'rows': '18'}), required=False,
        help_text=_("Leaving this empty causes Django to look for a "
        "template with the given name and populate this field with its content."))

    def save(self, commit=True):
        tpl = super(TemplateAdminForm, self).save(commit)

        if not tpl.content:
            loaders = []
            for loader_name in settings.TEMPLATE_LOADERS:
                if loader_name == 'dbtemplates.loader.Loader':
                    continue  # we miss dbtemplates
                loader = find_template_loader(loader_name)
                if loader is not None:
                    loaders.append(loader)
            for loader in loaders:
                try:
                    tpl_source, file_path = loader.load_template_source(tpl.name)
                    tpl.content = tpl_source
                    break
                except TemplateDoesNotExist:
                    pass  # continue to next loader
        if commit:
            tpl.save()
        return tpl

    class Meta:
        model = Template
        exclude = ('sites', 'creation_date', 'last_changed', )
