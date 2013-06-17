import hashlib
import random

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.db import models
from django.template.loader import render_to_string
from django.template import TemplateDoesNotExist

from .utils import send_email

# app settings
SIGNUP_ACTIVATION_DAYS = getattr(settings, 'SIGNUP_ACTIVATION_DAYS', 2)
SIGNUP_FORM_CLASS = getattr(settings, 'SIGNUP_FORM_CLASS', None)

class ValidationManager(models.Manager):
	def create_validation(self, user):
		v = Validation(user=user)

		salt = hashlib.sha256(str(random.random())).hexdigest()
		key = hashlib.sha256(salt + user.get_full_name()).hexdigest()

		v.key = key
		v.save(using=self._db)
		return v
	
	def create_inactive_user(self, **kwargs):
		UserModel = get_user_model()
		fields = [UserModel.USERNAME_FIELD] + UserModel.REQUIRED_FIELDS

		# Make sure that all required fields are submitted to create_user
		user_kwargs = {key: kwargs[key] for key in fields}
		for p in ['password', 'password1', 'password2']:
			if kwargs.get(p):
				user_kwargs['password'] = kwargs[p]
				break

		user = UserModel.objects.create_user(**user_kwargs)
		user.is_active = False
		user.save(using=self._db)

		return user
	
class Validation(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, unique=True)
	key = models.CharField(max_length=64)
	created = models.DateTimeField(auto_now_add=True)

	objects = ValidationManager()

	def get_activation_url(self, site):
		url = "http://%(site)s%(path)s" % {
			'site': site,
			'path': reverse('signup_activate', kwargs={'activation_key': self.key})
		}

		return url

	def send_activation_email(self, site):
		template_name = 'registration/activation_email.txt'

		# context data
		url = self.get_activation_url(site)
		context = {
			'site': site,
			'url': url,
			'activation_days': SIGNUP_ACTIVATION_DAYS
		}

		to = self.user.email

		send_email(template_name, context, to)
	
	def activate_user(self):
		self.user.is_active = True
		self.user.save()

