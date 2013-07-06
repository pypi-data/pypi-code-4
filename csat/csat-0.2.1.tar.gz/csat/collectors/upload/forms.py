from csat.acquisition import forms
from . import models


class ConfigForm(forms.CollectorConfigForm):
    class Meta(forms.CollectorConfigForm.Meta):
        model = models.UploadConfig
