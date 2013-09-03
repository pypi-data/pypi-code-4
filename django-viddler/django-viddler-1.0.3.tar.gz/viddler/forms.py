# -*- coding: utf-8 -*-
from django import forms

from .models import ViddlerVideo


class ViddlerUploadForm(forms.ModelForm):
    uploadtoken = forms.CharField(max_length=30, widget=forms.HiddenInput)
    callback = forms.CharField(max_length=255, widget=forms.HiddenInput, initial="")
    title = forms.CharField(max_length=255)
    description = forms.CharField(widget=forms.TextInput)
    slug = forms.CharField(max_length=255)
    file = forms.FileField()

    class Meta:
        model = ViddlerVideo
        exclude = ('age_limit', 'permalink', 'tags', 'view_permission',
            'embed_permission', 'tagging_permission', 'commenting_permission',
            'download_permission')
