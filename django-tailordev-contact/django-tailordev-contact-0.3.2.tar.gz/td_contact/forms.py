# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext as _

from .utils import get_rules_choices


class ContactForm(forms.Form):
    """
    The core contact form
    """
    first_name = forms.CharField(label=_("First name"), max_length=200,
                                 required=False)
    last_name = forms.CharField(label=_("Last name"), max_length=200,
                                required=False)
    sender = forms.EmailField(label=_("Your email address"))
    recipient_id = forms.IntegerField(required=False,
                                      widget=forms.HiddenInput())
    subject = forms.ChoiceField(label=_("Subject"),
                                choices=get_rules_choices())
    message = forms.CharField(label=_("Message"), widget=forms.Textarea)
