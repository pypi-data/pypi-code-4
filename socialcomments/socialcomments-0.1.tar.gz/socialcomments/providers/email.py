from socialcomments.providers import ProviderBase
from socialcomments.forms import CommentForm
from django.conf import settings
from django import forms
from django.contrib.sites.models import Site
from hashlib import md5
import requests, logging

AKISMET_URL = 'http://%s.rest.akismet.com/1.1/comment-check'
LOGGER = logging.getLogger('socialcomments')

class EmailForm(CommentForm):
	identity = forms.EmailField()
	
	def __init__(self, *args, **kwargs):
		super(EmailForm, self).__init__(*args, **kwargs)
		self.fields['name'].label = u'Your name'
		self.fields['identity'].label = u'Email address'
		self.fields['identity'].help_text = u'It won\'t be shared'
	
	class Meta(CommentForm.Meta):
		fields = ('name', 'identity', 'website', 'body')

class EmailProvider(ProviderBase):
	verbose_name = 'email'
	icon = 'envelope'
	form = EmailForm
	
	def check_for_spam(self, comment, request):
		akismet = getattr(settings, 'AKISMET_KEY', '')
		if not akismet:
			return False # Can't tell, so mark as not spam
		
		LOGGER.debug('Checking comment for spam')
		ip = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR')
		user_agent = request.META.get('USER_AGENT')
		referrer = request.META.get('HTTP_REFERER')
		
		site = Site.objects.get_current()
		response = requests.post(AKISMET_URL % akismet,
			data = {
				'blog': 'http://%s/' % (site.domain),
				'user_ip': ip,
				'user_agent': user_agent,
				'referrer': referrer,
				'permalink': 'http://%s%s' % (site.domain, comment.content_object.get_absolute_url()),
				'comment_type': 'comment',
				'comment_author': comment.name,
				'comment_author_email': comment.identity,
				'comment_author_url': comment.website,
				'comment_content': comment.body
			}
		)
		
		if response.content == 'true':
			return True
		
		if response.content == 'false':
			return False
		
		LOGGER.warn('Unexpected response from Akismet: %s' % response.content)
	
	def get_avatar(self, identity, size):
		return 'http://www.gravatar.com/avatar/%s.jpg?d=identicon&s=%d' % (
			md5(identity.lower()).hexdigest(), int(size)
		)