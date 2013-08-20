from django import forms

from .models import Timeline

class TimelineForm(forms.ModelForm):
    item_data = forms.CharField(widget=forms.HiddenInput)
    class Meta:
        model = Timeline
        exclude = ('slug',)
