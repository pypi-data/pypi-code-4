from django import forms
from django.db.models import get_model

import widgets

class S4DriveFileField(forms.CharField):
    def __init__(self, url, drive_static_url, **kwargs):
        defaults = {
            'widget': widgets.S4DriveFileWidget(url, drive_static_url),
        }
        defaults.update(kwargs)
        super(S4DriveFileField, self).__init__(**defaults)