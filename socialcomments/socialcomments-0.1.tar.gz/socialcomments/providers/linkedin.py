from socialcomments.providers import OAuthProviderBase
from elementtree import ElementTree
from oauth2 import Consumer, Token, Client
import requests

class LinkedInProvider(OAuthProviderBase):
	verbose_name = 'LinkedIn'
	icon = 'linkedin'
	authorise_url = 'https://www.linkedin.com/uas/oauth2/authorization?response_type=code&client_id=%(key)s&scope=r_emailaddress&redirect_uri=%(redirect)s&state=%(state)s'
	access_token_url = 'https://www.linkedin.com/uas/oauth2/accessToken?grant_type=authorization_code&code=%(code)s&redirect_uri=%(redirect)s&client_id=%(key)s&client_secret=%(secret)s'
	identity_url = 'https://api.linkedin.com/v1/people/~:(id,first-name,last-name)?oauth2_access_token=%s'
	
	def get_avatar(self, id, size):
		return ''
	
	def get_identity(self, access_token):
		response = requests.get(self.identity_url % access_token['access_token'])
		person = ElementTree.fromstring(response.content)
		
		return {
			'display_name': person.find('first-name').text + ' ' + person.find('last-name').text,
			'id': person.find('id').text,
			'url': 'http://www.linkedin.com/profile/view?id=%s' % person.find('id').text
		}