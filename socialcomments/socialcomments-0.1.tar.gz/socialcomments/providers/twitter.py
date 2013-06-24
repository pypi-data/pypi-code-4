from django.contrib.sites.models import Site
from django.utils.http import urlquote
from django.utils import simplejson
from django.core.urlresolvers import reverse
from urlparse import parse_qs
from socialcomments.providers import OAuthProviderBase
from socialcomments.forms import OAuthCommentForm
from django import forms
from oauth2 import Consumer, Token, Client

class TwitterForm(OAuthCommentForm):
	post = forms.BooleanField(
		required = False,
		label = u'Post to Twitter'
	)

class TwitterProvider(OAuthProviderBase):
	verbose_name = 'Twitter'
	icon = 'twitter'
	template = 'socialcomments/form/twitter.inc.html'
	request_token_url = 'https://api.twitter.com/oauth/request_token'
	authorise_url = 'https://api.twitter.com/oauth/authorize?oauth_token=%s'
	access_token_url = 'https://api.twitter.com/oauth/access_token'
	identity_url = 'https://api.twitter.com/1.1/account/verify_credentials.json'
	post_url = 'https://api.twitter.com/1.1/statuses/update.json'
	form = TwitterForm
	
	def consumer(self):
		return Consumer(
			key = self.key,
			secret = self.secret
		)
	
	def connect(self):
		client = Client(self.consumer())
		response, content = client.request(self.request_token_url, 'POST',
			body = 'oauth_callback=%s' % urlquote(
				'http://%s%s?p=%s.%s' % (
					Site.objects.get_current().domain,
					reverse('socialcomments_callback'),
					self.__module__, type(self).__name__
				)
			)
		)
		
		try:
			details = parse_qs(content)
		except:
			raise Exception('Unrecognised response')
		
		if not 'oauth_token' in details:
			raise Exception('Site has not returned an OAuth token')
		
		return self.redirect(
			self.authorise_url % ''.join(details['oauth_token'])
		)
	
	def finalise_connection(self, **kwargs):
		client = Client(self.consumer())
		
		response, content = client.request(self.access_token_url, 'POST',
			body = 'oauth_token=%s&oauth_verifier=%s' % (
				urlquote(kwargs['oauth_token']),
				urlquote(kwargs['oauth_verifier'])
			)
		)
		
		try:
			details = parse_qs(content)
		except:
			raise Exception('Unrecognised response')
		
		if not 'oauth_token' in details:
			raise Exception('Site has not returned an OAuth token')
		
		if not 'oauth_token_secret' in details:
			raise Exception('Site has not returned an OAuth secret')
		
		return details
	
	def get_avatar(self, id, size):
		return 'http://twitter.com/api/users/profile_image/%s' % id
	
	def get_identity(self, access_token):
		token = Token(
			key = ''.join(access_token.get('oauth_token')),
			secret = ''.join(access_token.get('oauth_token_secret')),
		)
		
		client = Client(self.consumer(), token)
		response, content = client.request(self.identity_url, 'GET')
		json = simplejson.loads(content)
		
		if json:
			if 'error' in json:
				raise Exception('An error occurred obtaining the identity')
			
			return {
				'username': json['screen_name'],
				'display_name': json['name'],
				'url': u'http://twitter.com/%s' % json['screen_name'],
				'id': json['id']
			}
		
		raise Exception(json)
	
	def post(self, obj, access_token):
		site = Site.objects.get_current()
		
		token = Token(
			key = ''.join(access_token.get('oauth_token')),
			secret = ''.join(access_token.get('oauth_token_secret')),
		)
		
		title = unicode(obj)
		content_type = unicode(obj._meta.verbose_name)
		url = self.shorten_url('http://%s%s' % (site.domain, obj.get_absolute_url()))
		prefix = 'I\'ve just commented on the '
		pattern = u'%s%s %s %s'
		title_avail = 140 - len(prefix) - (len(url) + 1) - (len(content_type) + 1)
		
		while len(title) > title_avail:
			before_space, space, after_space = title[:title_avail - 3].rpartition(' ')
			title = before_space + '...'
		
		text = pattern % (prefix, content_type, title, url)
		client = Client(self.consumer(), token)
		response, content = client.request(self.post_url, 'POST',
			body = 'status=%s' % urlquote(text)
		)
		
		json = simplejson.loads(content)
		if json.get('error'):
			raise Exception(resp['error'])
		
		if json.get('id'):
			return True
		
		raise Exception(json)