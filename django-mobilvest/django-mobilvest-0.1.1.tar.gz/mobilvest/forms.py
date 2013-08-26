# -*- coding: utf8 -*-
from django import forms

__author__ = 'ir4y'

class SendSMSForm(forms.Form):
    phone = forms.CharField()
    text = forms.CharField(widget=forms.Textarea)
