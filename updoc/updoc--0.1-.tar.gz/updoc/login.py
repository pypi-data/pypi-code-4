from django import forms
from django.utils.translation import ugettext_lazy as _

__author__ = 'flanker'


class LoginForm(forms.Form):
    """Upload form"""
    username = forms.CharField(label=_('Name'), max_length=240)
    password = forms.CharField(label=_('Keywords'), max_length=255, required=False)


def login(request):
    pass
