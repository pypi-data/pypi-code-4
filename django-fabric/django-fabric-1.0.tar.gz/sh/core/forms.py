# -*- coding: utf-8 -*-
from django import forms

class RegistrationForm (forms.Form):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True,max_length=30)
    last_name = forms.CharField(required=True, max_length=30)