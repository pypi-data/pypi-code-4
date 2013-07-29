from crispy_forms import layout

from csat.acquisition import forms
from . import models


class ConfigForm(forms.CollectorConfigForm):

    class Meta(forms.CollectorConfigForm.Meta):
        model = models.RandomConfig

    def get_basic_layout(self):
        return layout.Layout(
            layout.Field('domains'),
            layout.Field('nodes'),
            layout.Field('edges'),
        )

    def get_advanced_layout(self):
        return layout.Layout(
            layout.Field('ratio'),
            layout.Field('seed'),
        )
