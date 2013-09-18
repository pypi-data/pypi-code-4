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

import hashlib
import random
import os
import datetime
import re
import string

from django.db import models, transaction
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site

ACTIVATION_CODE_REGEX = '[' + string.hexdigits + ']{32}'

class UserSignupManager(models.Manager):
	def activate(self, activation_code):
		if re.match(ACTIVATION_CODE_REGEX, activation_code):
			try:
				signup = self.get(activation_code=activation_code)
			except self.model.DoesNotExist:
				return None

			user = signup.user
			user.is_active = True
			user.save()
			signup.delete()
			return user
		return None

	def signup(self, cleaned_data):
		user_model = get_user_model()
		user_fields = {}
		for field in user_model._meta.get_all_field_names():
			if field in cleaned_data:
				user_fields[field] = cleaned_data[field]
		user = user_model.objects.create_user(**user_fields)
		user.is_active = False
		user.save()

		email = user.email
		if isinstance(email, unicode):
			email = email.encode('utf-8')
		salt = os.urandom(256)
		signup = self.create(user=user, activation_code=hashlib.sha256(email + salt).hexdigest()[:32])
		signup.send_activation_email()

		return user

	signup = transaction.commit_on_success(signup)

class UserSignup(models.Model):
	user = models.ForeignKey(get_user_model(), unique=True, verbose_name=_('User'))
	activation_code = models.CharField(max_length=32)

	objects = UserSignupManager()

	def send_activation_email(self):
		context = {'activation_code': self.activation_code, 'site': Site.objects.get_current()}
		subject = ' '.join(render_to_string('accounts/activation_email_subject.txt', context).splitlines())
		message = render_to_string('accounts/activation_email_message.html', context)
		self.user.email_user(subject, message)

	class Meta:
		verbose_name = _('user signup')
		verbose_name_plural = _('user signups')