# Copyright 2013 Binary Birch Tree
# http://www.binarybirchtree.com

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit

import settings


class BaseProfileForm(forms.Form):
	required_css_class = 'required'

	first_name = forms.RegexField(
		regex=r'^[a-zA-Z-]+$',
		max_length=30,
		label=_('First name'),
		error_messages={'invalid': _('The name you entered contains invalid characters.')}
	)

	last_name = forms.RegexField(
		regex=r'^[a-zA-Z-]+$',
		max_length=30,
		label=_('Last name'),
		error_messages={'invalid': _('The name you entered contains invalid characters.')}
	)

	# Properly capitalize names.
	def clean_first_name(self):
		return self.cleaned_data['first_name'].title()

	def clean_last_name(self):
		return self.cleaned_data['last_name'].title()


class ProfileForm(BaseProfileForm):
	def __init__(self, *args, **kwargs):
		self.helper = FormHelper()
		self.helper.form_class = 'edit-profile-form'
		self.helper.form_method = 'post'
		self.helper.layout = Layout(
			Fieldset('', 'first_name', 'last_name'),
			Submit('submit', _('Save Changes')),
		)
		super(ProfileForm, self).__init__(*args, **kwargs)


class BasePasswordForm(forms.Form):
	password = forms.CharField(widget=forms.PasswordInput, label=_('Password'))
	password_confirm = forms.CharField(widget=forms.PasswordInput, label=_('Confirm password'))

	def clean(self):
		# Verify that the passwords match
		if 'password' in self.cleaned_data and 'password_confirm' in self.cleaned_data:
			if self.cleaned_data['password'] != self.cleaned_data['password_confirm']:
				raise forms.ValidationError(_('The passwords you entered do not match.'))

		return self.cleaned_data


class SignupForm(BaseProfileForm, BasePasswordForm):
	email = forms.EmailField(label=_('Email'))

	if settings.ACCOUNTS_SIGNUP_REQUIRE_CAPTCHA:
		from captcha.fields import ReCaptchaField

		captcha = ReCaptchaField(attrs={'theme': 'clean'}, label='')

	def clean_email(self):
		user = get_user_model().objects.filter(email=self.cleaned_data['email'])
		if user.exists():
			raise forms.ValidationError(_('The email you provided is already in use.'))

		return self.cleaned_data['email']