import base64
from urllib import urlencode
from urllib2 import Request, HTTPError

from django.utils import simplejson

from social_auth.utils import dsa_urlopen
from social_auth.exceptions import AuthTokenError
from social_auth.backends import BaseOAuth2, OAuthBackend


class BratabaseBackend(OAuthBackend):
    """Bratabase OAuth2 authentication backend"""
    name = 'bratabase'
    # Default extra data to store

    EXTRA_DATA = [
        ('user_id', 'user_id'),
    ]

    def get_user_id(self, details, response):
        return response['body']['user_id']

    def get_user_details(self, response):
        """Return user details from Bratabase account"""
        body = response['body']
        return {
            'username': body['username'],
            'email': body.get('email')
        }


class BratabaseAuth(BaseOAuth2):
    """Bratabase OAuth2 support"""
    REDIRECT_STATE = False
    AUTH_BACKEND = BratabaseBackend
    SCOPE_SEPARATOR = ' '
    SETTINGS_KEY_NAME = 'BRATABASE_APP_ID'
    SETTINGS_SECRET_NAME = 'BRATABASE_API_SECRET'
    SCOPE_VAR_NAME = 'BRATABASE_EXTENDED_PERMISSIONS'
    DEFAULT_SCOPE = ['identity']
    ME_URL = 'https://api.bratabase.com/me/'
    AUTHORIZATION_URL ='http://www.bratabase.com/oauth/authorize/'
    ACCESS_TOKEN_URL = 'http://www.bratabase.com/oauth/token/'

    @classmethod
    def refresh_token(cls, token, redirect_uri):
        data = cls.refresh_token_params(token)
        data['redirect_uri'] = redirect_uri
        request = Request(cls.ACCESS_TOKEN_URL,
                          data=urlencode(data),
                          headers=cls.auth_headers())
        return cls.process_refresh_token_response(dsa_urlopen(request).read())

    def user_data(self, access_token, *args, **kwargs):
        """Grab user profile information from Bratabase."""
        try:
            request = Request(self.ME_URL,
                headers={'Authorization': 'bearer %s' % access_token}
            )
            return simplejson.load(dsa_urlopen(request))
        except ValueError:
            return None
        except HTTPError:
            raise AuthTokenError(self)

    @classmethod
    def auth_headers(cls):
        return {
            'Authorization': 'Basic %s' % base64.urlsafe_b64encode(
                '%s:%s' % cls.get_key_and_secret()
            )
        }

    def auth_complete(self, *args, **kwargs):
        if 'access_token' in self.data:
            kwargs['response'] = dict(self.data.copy())
            return self.do_auth(self.data['access_token'], *args, **kwargs)

        return super(BratabaseAuth, self).auth_complete(*args, **kwargs)


BACKENDS = {
    'bratabase': BratabaseAuth
}
