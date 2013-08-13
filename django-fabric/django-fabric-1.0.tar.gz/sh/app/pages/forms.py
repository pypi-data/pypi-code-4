# -*- coding: utf-8 -*-
from django import forms
from sh.app.pages.models import Page


class PageForm(forms.ModelForm):
    class Meta:
        model = Page
        exclude = ('is_active', 'shorten_url', 'category')
        fields = ('title', 'menu_title', 'slug', 'content', 'weight')

    def __init__(self, *args, **kwargs):
        super(PageForm, self).__init__(*args, **kwargs)
        self.fields['slug'].widget.attrs['readonly'] = 'readonly'
