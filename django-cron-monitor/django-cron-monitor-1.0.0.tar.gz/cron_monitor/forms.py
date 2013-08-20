from django import forms
from cron_monitor.models import EmailSettings


class SettingsForm(forms.ModelForm):
    class Meta:
        model = EmailSettings
        widgets = {
            'email_host_password': forms.PasswordInput()
        }
