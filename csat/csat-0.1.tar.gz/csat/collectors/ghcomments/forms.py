from crispy_forms import layout

from csat.acquisition import forms
from . import models


class ConfigForm(forms.CollectorConfigForm):

    class Meta(forms.CollectorConfigForm.Meta):
        model = models.GithubCommentsConfig

    def get_basic_layout(self):
        return layout.Layout(
            layout.Field('repo_name'),
            layout.Field('access_token'),
        )

    def get_advanced_layout(self):
        return layout.Layout(
            layout.Field('issue_nodes'),
            layout.Field('issues_state'),
        )
