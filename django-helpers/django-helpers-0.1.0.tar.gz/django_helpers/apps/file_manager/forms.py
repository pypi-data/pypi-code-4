# coding=utf-8
from django import forms
from django_helpers.apps.form_renderer import FormRenderer
from models import File

__author__ = 'ajumell'


class AddFileForm(forms.ModelForm):
    class Meta:
        model = File

class EditFileForm(forms.ModelForm):
    class Meta:
        model = File
        exclude = ('image', )


class AddFileFormRenderer(FormRenderer):
    form_id = 'add-file-form'
    form_submit = 'Upload File'
