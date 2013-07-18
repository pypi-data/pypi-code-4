from django import forms
from .models import InboxSMS


class InboxSMSForm(forms.ModelForm):
    class Meta:
        model = InboxSMS
