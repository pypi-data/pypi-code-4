from django import forms
from django.forms.models import ModelForm

from .models import PodcastChannel


class CreateChannelForm(ModelForm):
    class Meta:
        model = PodcastChannel
        fields = ('url',)
        widgets = {'url': forms.widgets.TextInput(attrs={'placeholder': 'Channel URL'})}

