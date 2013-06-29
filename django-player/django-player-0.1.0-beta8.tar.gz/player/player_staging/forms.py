from django import forms
from django.utils.translation import ugettext as _

from player.base.forms import BaseForm

from staging.models import StagingServer


class StagingServerForm(BaseForm, forms.ModelForm):

    class Meta:
        model = StagingServer


class CreateRepoFromServerForm(BaseForm, forms.Form):
    hostname = forms.CharField(widget=forms.RadioSelect)

    def __init__(self, *args, **kwargs):
        super(CreateRepoFromServerForm, self).__init__(*args, **kwargs)
        server_choices = []
        for server in StagingServer.objects.all():
            label = server.name
            is_ok, message = server.check_repository()
            if not is_ok:
                label += ". %s: %s" % (_('Be careful'), message)
            server_choices.append((server.hostname, label))
        self.fields['hostname'].widget.choices = server_choices
