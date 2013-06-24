from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.conf import settings
from django.utils.http import urlquote
from django.utils.timezone import now
from urlparse import parse_qs
from pyquery import PyQuery
from html2text import HTML2Text
from markdown import markdown as md
from socialcomments.forms import CommentForm, OAuthCommentForm
from time import mktime
import requests

UNCLEAN_TAGS = (
	'audio', 'video', 'iframe', 'object', 'form', 'input', 'select', 'textarea', 'script', 'style'
)

UNCLEAN_ATTRS = (
	'onafterprint', 'onbeforeprint', 'onbeforeunloa', 'onerro', 'onhaschange', 'onload', 'onmessageNew',
	'onoffline', 'ononline', 'onpagehide', 'onpageshow', 'onpopstate', 'onredo', 'onresize', 'onstorage', 'onundo',
	'onunload'
)

if 'bambu.urlshortener' in settings.INSTALLED_APPS:
	from bambu.urlshortener import shorten
else:
	shorten = lambda u: u

class ProviderBase(object):
	verbose_name = 'base'
	icon = 'comment'
	form = CommentForm
	template = 'socialcomments/form/base.inc.html'
	
	def shorten_url(self, url):
		return shorten(url)
	
	def get_form(self, *args, **kwargs):
		return self.form(*args, **kwargs)
	
	def check_for_approval(self, comment):
		return type(comment).objects.filter(
			identity__iexact = comment.identity,
			provider = comment.provider,
			approved = True,
			spam = False
		).exists()
	
	def check_for_spam(self, comment, request):
		return False # not spam
	
	def sanitise(self, text, markdown = True):
		if markdown:
			text = md(text)
		
		dom = PyQuery(text)
		
		for a in dom.find('a[href^="javascript:"]'):
			a = PyQuery(a)
			a.replaceWith(a.text())

		for obj in UNCLEAN_TAGS:
			dom.find(obj).remove()

		for attr in UNCLEAN_ATTRS:
			dom.find('[%s]' % attr).removeAttr(attr)
		
		text = dom.outerHtml()
		if markdown:
			dom = HTML2Text()
			text = dom.handle(text)

		return text
	
	def get_avatar(self, identity, size):
		raise NotImplementedError('Method not implemented.')
	
	def post(self, obj, access_token):
		raise NotImplementedError('Method not implemented.')

class OAuthProviderBase(ProviderBase):
	form = OAuthCommentForm
	template = 'socialcomments/form/oauth.inc.html'
	verbose_name = u'OAuth'
	code_qs_parameter = 'code'
	oauth_token_qs_parameter = 'oauth_token'
	oauth_verifier_qs_parameter = 'oauth_verifier'
	
	def __init__(self, *args, **kwargs):
		super(OAuthProviderBase, self).__init__(*args, **kwargs)
		social_providers = getattr(settings, 'SOCIAL_COMMENTS_PROVIDERS', ())
		
		for p in social_providers:
			if p[0] == '%s.%s' % (self.__module__, type(self).__name__):
				self.key = p[1].get('CONSUMER_KEY')
				self.secret = p[1].get('CONSUMER_SECRET')
				return
	
	def redirect(self, url):
		return HttpResponseRedirect(url)
	
	def get(self, *args, **kwargs):
		return requests.get(*args, **kwargs)
	
	def get_url_parameters(self):
		return {
			'key': self.key,
			'secret': self.secret,
			'redirect': urlquote(
				'http://%s%s?p=%s.%s' % (
					Site.objects.get_current().domain,
					reverse('socialcomments_callback'),
					self.__module__, type(self).__name__
				)
			),
			'state': mktime(now().timetuple())
		}
	
	def connect(self):
		return self.redirect(
			self.authorise_url % self.get_url_parameters()
		)
	
	def finalise_connection(self, **kwargs):
		params = self.get_url_parameters()
		code = kwargs.get(self.code_qs_parameter)
		oauth_token = kwargs.get(self.oauth_token_qs_parameter)
		oauth_verifier = kwargs.get(self.oauth_verifier_qs_parameter)
		params[self.code_qs_parameter] = code
		response = self.get(self.access_token_url % params)
		
		try:
			json = (callable(response.json) and response.json()) or response.json
			if json:
				return json
		except:
			pass
		
		try:
			return dict(
				(key, value[0])
				for key, value in parse_qs(response.text).items()
			)
		except:
			raise Exception('Unrecognised response')
	
	def post(self, obj, access_token):
		pass