# coding: utf-8
from django import forms
from django.utils.translation import ugettext_lazy as _
from search_statistic.models import SearchQuery, Visit


class SearchQueryForm(forms.ModelForm):

    class Meta:
        model = SearchQuery


class VisitForm(forms.ModelForm):

    visited_object = forms.CharField(label=_('visited object'))

    def __init__(self, *a, **k):
        super(VisitForm, self).__init__(*a, **k)
        self.fields['visited_object'].initial = self.instance.visited_object

    class Meta:
        model = Visit
