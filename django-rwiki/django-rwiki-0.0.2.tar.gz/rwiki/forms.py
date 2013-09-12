# -*- coding: utf-8 -*-
from django import forms
import models as mymodels
from django.core.files.images import get_image_dimensions

class PageForm(forms.ModelForm):

    comment = forms.CharField(required=False)

    class Meta:
        model = mymodels.Page
        exclude = ('hits', 'owner')
