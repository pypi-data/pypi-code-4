from django import forms
from django.core.urlresolvers import reverse

from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import FormActions
from crispy_forms.layout import Layout, Fieldset, Field, Submit, Div

from ftp_deploy.models import Service


class ServiceForm(forms.ModelForm):

    """Add/Edit service form"""

    def __init__(self, *args, **kwargs):
        super(ServiceForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'service-form'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-6'

        self.helper.layout = Layout(
            Fieldset('FTP Settings',
                     'ftp_host',
                     'ftp_username',
                     'ftp_password',
                     'ftp_path'
                     ),
            Fieldset('Repository',
                     Field('repo_source', data_action=reverse('ftpdeploy_bb_api', args=(0,))),
                     'repo_name',
                     'repo_slug_name',
                     'repo_branch'
                     ),
            Fieldset('Security',
                     'secret_key'
                     ),

            Div(
                Submit('save', 'Submit', css_class='pull-right'),
                css_class='col-sm-8'
            )

        )

    class Meta:
        model = Service
        exclude = ['status', 'status_date', 'status_message']
        widgets = {
            'ftp_password': forms.PasswordInput(render_value=True),
        }
