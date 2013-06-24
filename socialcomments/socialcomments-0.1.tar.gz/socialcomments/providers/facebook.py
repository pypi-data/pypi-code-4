from socialcomments.providers import OAuthProviderBase
import requests

class FacebookProvider(OAuthProviderBase):
	verbose_name = 'Facebook'
	icon = 'facebook'
	authorise_url = 'https://www.facebook.com/dialog/oauth?client_id=%(key)s&redirect_uri=%(redirect)s&scope=publish_actions'
	access_token_url = 'https://graph.facebook.com/oauth/access_token?client_id=%(key)s&redirect_uri=%(redirect)s&client_secret=%(secret)s&code=%(code)s'
	identity_url = 'https://graph.facebook.com/me?access_token=%s'
	
	def get_avatar(self, id, size):
		return 'http://graph.facebook.com/%s/picture?width=%d&height=%d' % (id, size, size)
	
	def get_identity(self, access_token):
		response = requests.get(self.identity_url % access_token['access_token'])
		json = (callable(response.json) and response.json()) or response.json
		
		if json:
			if 'error' in json:
				raise Exception('An error occurred obtaining the identity')
			
			return {
				'username': json['username'],
				'display_name': json['name'],
				'url': json['link'],
				'id': json['id']
			}
		
		raise Excepteion('Unexpected response')