from django import forms

from .models import Feed, Category


class AddFeedForm(forms.ModelForm):
    class Meta:
        model = Feed
        exclude = ('user', 'title')


class ImportFeedForm(forms.Form):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ImportFeedForm, self).__init__(*args, **kwargs)

        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user)

    archive = forms.FileField(label='Google takeout zip file')
    category = forms.ModelChoiceField(
        label="Default category", queryset=Category.objects.filter(user=None),
        widget=forms.Select())
