from django import forms
from django.conf import settings
from django.utils.importlib import import_module
from socialcomments.models import Comment

class CommentForm(forms.ModelForm):
	provider = forms.CharField(
		widget = forms.HiddenInput
	)
	
	identity = forms.CharField(
		widget = forms.HiddenInput
	)
	
	def __init__(self, *args, **kwargs):
		super(CommentForm, self).__init__(*args, **kwargs)
		self.fields['body'].label = u'Your comment'
	
	def save(self, commit = True):
		obj = super(CommentForm, self).save(commit = False)
		obj.provider = self.cleaned_data.get('provider')
		obj.sanitise()
		
		if commit:
			obj.save()
		
		return obj
	
	class Meta:
		model = Comment
		fields = ('name', 'website', 'identity', 'body',)

class OAuthCommentForm(CommentForm):
	name = forms.CharField(
		widget = forms.HiddenInput
	)
	
	website = forms.CharField(
		widget = forms.HiddenInput
	)