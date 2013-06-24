from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.conf import settings
from django.utils.importlib import import_module
from socialcomments.managers import *
from socialcomments.helpers import get_provider_choices

if 'bambu.notifications' in settings.INSTALLED_APPS:
	from bambu import notifications
else:
	from bambu.mail.shortcuts import render_to_mail

MARKDOWN = getattr(settings, 'COMMENTS_MARKDOWN', True)

class Comment(models.Model):
	name = models.CharField(max_length = 50)
	website = models.URLField(max_length = 255, null = True, blank = True)
	provider = models.CharField(max_length = 100, db_index = True, choices = get_provider_choices())
	identity = models.CharField(max_length = 255, db_index = True)
	sent = models.DateTimeField(auto_now_add = True, db_index = True)
	approved = models.BooleanField(default = False, db_index = True)
	spam = models.BooleanField(default = False, db_index = True)
	body = models.TextField()
	content_type = models.ForeignKey(ContentType)
	object_id = models.PositiveIntegerField(db_index = True)
	content_object = generic.GenericForeignKey()
	objects = CommentManager()
	
	def __unicode__(self):
		return u'Re: %s' % unicode(self.content_object)
	
	def get_absolute_url(self):
		return self.content_object.get_absolute_url() + '#comment-%d' % self.pk
	
	def get_provider(self):
		if not getattr(self, '_provider', None):
			module, dot, klass = self.provider.rpartition('.')
			module = import_module(module)
			self._provider = getattr(module, klass)
		
		return self._provider
	
	def get_avatar(self, size = 50):
		provider = self.get_provider()
		return provider().get_avatar(self.identity, size)
	
	@property
	def icon(self):
		provider = self.get_provider()
		return provider.icon
	
	def check_for_spam(self, request):
		provider = self.get_provider()
		return provider().check_for_spam(self, request)
	
	def check_for_approval(self):
		provider = self.get_provider()
		return provider().check_for_approval(self)
	
	def post_to_profile(self):
		provider = self.get_provider()
		return provider().post(self)
	
	def sanitise(self, markdown = False):
		provider = self.get_provider()
		self.body = provider().sanitise(self.body, markdown)
	
	def save(self, *args, **kwargs):
		notify = kwargs.pop('notify', True)
		
		if self.spam:
			self.approved = False
		
		new = not self.pk and not self.spam
		if new and not self.approved and not self.spam:
			self.approved = self.check_for_approval()
		
		super(Comment, self).save(*args, **kwargs)
		
		if new and notify:
			if not 'bambu.notifications' in settings.INSTALLED_APPS:
				render_to_mail(
					u'New comment submitted',
					'socialcomments/mail.txt',
					{
						'comment': self,
						'author': self.content_object.author
					},
					self.content_object.author
				)
			else:
				notifications.notify('socialcomments.comment_posted',
					self.content_object.author,
					comment = self,
					actions = [
						{
							'urlname': 'admin:comments_comment_change',
							'args': [self.pk],
							'title': 'View the comment'
						}
					]
				)
	
	class Meta:
		ordering = ('-sent',)
		get_latest_by = 'sent'
	
	class QuerySet(models.query.QuerySet):
		def live(self):
			return self.filter(
				approved = True,
				spam = False
			)