from __future__ import absolute_import

from django import forms
from django.utils.translation import ugettext_lazy as _

from crispy_forms import layout, helper, bootstrap
from csat.django.apps.bootstrap.layout import ButtonLink

from . import models


class BasicPanel(layout.Layout):
    def render(self, *args, **kwargs):
        html = super(BasicPanel, self).render(*args, **kwargs)
        return '<div class="front-panel">{}</div>'.format(html)


class AdvancedPanel(layout.Layout):
    def render(self, *args, **kwargs):
        html = super(AdvancedPanel, self).render(*args, **kwargs)
        return '<div class="back-panel">{}</div>'.format(html)


class CollectorFormTitle(layout.Layout):
    def render(self, form, form_style, context):
        html = u'<h1 class="form-title">{}</h1>'.format(
            context['collector'].name)
        return html


class SimpleLayoutMixin(object):
    def __init__(self, *args, **kwargs):
        super(SimpleLayoutMixin, self).__init__(*args, **kwargs)
        self.helper = helper.FormHelper()
        self.helper.layout = self.get_layout()
        self.helper.form_class = 'form-horizontal form-bordered'

    def get_layout(self):
        elements = [layout.Field(name) for name in self.fields.iterkeys()]
        elements += [
            bootstrap.FormActions(layout.Submit('submit', _('Submit')))
        ]
        return layout.Layout(*elements)


class AcquisitionSessionConfigForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.helper = helper.FormHelper()
        self.helper.layout = self.get_layout()
        super(AcquisitionSessionConfigForm, self).__init__(*args, **kwargs)

    def get_layout(self):
        return layout.Layout(
            layout.Field('name'),
            layout.Field('description'),
        )

    class Meta:
        model = models.AcquisitionSessionConfig
        fields = ['name', 'description', ]


class CollectorConfigForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.helper = helper.FormHelper()
        self.helper.layout = self.get_layout()
        self.helper.form_class = 'form-horizontal form-force-block-help'
        super(CollectorConfigForm, self).__init__(*args, **kwargs)
        self.fields.pop('session_config')

    class Meta:
        exclude = ('started', 'completed', 'running_instance_id', 'status',
                   'result', 'received', 'configurator',)

    def get_advanced_layout(self):
        return None

    def get_basic_layout(self):
        return None

    def get_layout(self):
        advanced_layout = self.get_advanced_layout()

        if advanced_layout:
            advanced_link = (
                '<li><a class="advanced" href="#"><i class="icon-wrench">'
                '</i>More options</a></li>'
            )
            advanced_panel = AdvancedPanel(
                self.get_advanced_layout(),
                bootstrap.FormActions(layout.Button('submit', _('Apply'),
                                                    css_class='btn-primary'),
                                      ButtonLink(_('Cancel'), url='#'),)
            )
        else:
            advanced_link = ''
            advanced_panel = layout.Layout()

        basic_layout = self.get_basic_layout()

        if not basic_layout:
            basic_layout = layout.Layout(
                layout.HTML('<p class="nooptions">This collector does not '
                            'have any configuration option.</p>')
            )

        basic_panel = BasicPanel(
            CollectorFormTitle(),
            layout.HTML(
                '<ul class="actions">{}<li><a class="remove" href="#">'
                '<i class="icon-remove"></i>Remove</a></li></ul>'.format(
                    advanced_link)
            ),
            basic_layout
        )

        return layout.Layout(basic_panel, advanced_panel)


class ResultsUploadForm(SimpleLayoutMixin, forms.ModelForm):

    successful = forms.BooleanField(required=False, initial=True)

    def __init__(self, *args, **kwargs):
        super(ResultsUploadForm, self).__init__(*args, **kwargs)
        self.fields['graph'].allow_empty_file = True
        self.fields['output'].allow_empty_file = True

    class Meta:
        model = models.DataCollectorConfig
        fields = ('graph', 'output')


class ThumbnailForm(forms.ModelForm):
    class Meta:
        model = models.AcquisitionSessionConfig
        fields = ('thumbnail', )
