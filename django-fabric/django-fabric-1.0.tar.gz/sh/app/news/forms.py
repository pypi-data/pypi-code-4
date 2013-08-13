# -*- coding: utf-8 -*-
from django import forms
from sh.app.news.models import NewsItem


class NewsItemForm(forms.ModelForm):
    class Meta:
        model = NewsItem
        fields = ('title', 'slug', 'pub_date', 'sticky','content')

    def __init__(self, *args, **kwargs):
        super(NewsItemForm, self).__init__(*args, **kwargs)
        self.fields['slug'].widget.attrs['readonly'] = 'readonly'
