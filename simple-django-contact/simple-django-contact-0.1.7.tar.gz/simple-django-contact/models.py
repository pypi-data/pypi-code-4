from django.db import models
from django import forms



class Contact(forms.Form):
	name = forms.CharField(widget=forms.TextInput(attrs={'class':'input-block-level',}))
	email = forms.EmailField(widget=forms.TextInput(attrs={'class':'input-block-level',}))
	message = forms.CharField(widget=forms.Textarea(attrs={'class':'input-block-level',}))