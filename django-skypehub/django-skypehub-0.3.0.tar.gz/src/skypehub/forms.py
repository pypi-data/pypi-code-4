# coding: utf-8
from django import forms


class PostMessageForm(forms.Form):
    message = forms.CharField()
    chat = forms.CharField()


class PostUserMessageForm(forms.Form):
    message = forms.CharField()
    username = forms.CharField()
