from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse, NoReverseMatch
from requests_oauthlib import OAuth1 as OAuth1Auth

import requests, shortuuid

try:
    from urllib import urlencode
    from urlparse import parse_qs 
except ImportError:
    from urllib.parse import parse_qs, urlencode
    

class OAuth1(object):
    def __init__(self,
                 client_id=None, client_secret=None, 
                 oauth_token=None, oauth_token_secret=None,
                 verifier=None,
                 request_token_url=None, authorization_url=None, access_token_url=None,
                 signature_type=None,
                 requests=requests):

        assert client_id, "Missing `client_id`"
        assert client_secret, "Missing `client_secret`"

        assert request_token_url, "Missing `request_token_url`"
        assert request_token_url.startswith('https://'), "`request_token_url` not SSL enabled"

        assert authorization_url, "Missing `authorization_url`"
        assert authorization_url.startswith('https://'), "`authorization_url` not SSL enabled"

        assert access_token_url, "Missing `access_token_url`"
        assert access_token_url.startswith('https://'), "`access_token_url` not SSL enabled"

        self.client_id = client_id
        self.client_secret = client_secret 

        self.oauth_token = oauth_token
        self.oauth_token_secret = oauth_token_secret

        self.verifier = verifier 

        self.request_token_url = request_token_url
        self.authorization_url = authorization_url
        self.access_token_url = access_token_url

        self.signature_type = signature_type or 'auth_header'

        self.requests = requests 


    @property 
    def auth(self):
        return OAuth1Auth(
            self.client_id,
            client_secret=self.client_secret,
            resource_owner_key=self.oauth_token,
            resource_owner_secret=self.oauth_token_secret,
            verifier=self.verifier,
            signature_type=self.signature_type)

    def get_request_token(self):

        response = self.requests.post(self.request_token_url, auth=self.auth)

        assert response.status_code == 200, response.content

        parsed = parse_qs(response.content)

        self.oauth_token, self.oauth_token_secret = (
            parsed['oauth_token'][0], parsed['oauth_token_secret'][0])

        return {'oauth_token': self.oauth_token,
                'oauth_token_secret': self.oauth_token_secret}
        
    def get_authorization_url(self):
        return u'{authorization_url}?{params}'.format(
            authorization_url=self.authorization_url,
            params=urlencode({'oauth_token': self.oauth_token}))


    def get_access_token(self):
        response = self.requests.post(self.access_token_url, auth=self.auth)

        assert response.status_code == 200, response.content

        parsed = parse_qs(response.content)

        self.oauth_token, self.oauth_token_secret = (
            parsed['oauth_token'][0], parsed['oauth_token_secret'][0])

        return {'oauth_token': self.oauth_token,
                'oauth_token_secret': self.oauth_token_secret}

    
