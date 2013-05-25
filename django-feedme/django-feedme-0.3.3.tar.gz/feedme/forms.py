from django import forms

from .models import Feed, Category


class AddFeedForm(forms.ModelForm):
    class Meta:
        model = Feed
        exclude = ('user', 'title')


class ImportFeedForm(forms.Form):
    archive = forms.FileField(label='Google takeout zip file')
    category = forms.ModelChoiceField(
        label="Default category", queryset=Category.objects.all(),
        widget=forms.Select())
