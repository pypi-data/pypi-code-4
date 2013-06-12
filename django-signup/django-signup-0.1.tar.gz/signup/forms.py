from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

class DefaultUserCreationForm(UserCreationForm):
	"""
	A form used to create a new user. This is only useful to the default user
	model, which has 'username', 'email' and 'password' fields.
	"""
	email = forms.EmailField(_('Email address'))

	def __init__(self, *args, **kwargs):
		super(DefaultUserCreationForm, self).__init__(*args, **kwargs)

		self.fields.keyOrder = [
			'username', 'email', 'password1', 'password2'
		]
