"""
Google OpenID and OAuth support

OAuth works straightforward using anonymous configurations, username
is generated by requesting email to the not documented, googleapis.com
service. Registered applications can define settings GOOGLE_CONSUMER_KEY
and GOOGLE_CONSUMER_SECRET and they will be used in the auth process.
Setting GOOGLE_OAUTH_EXTRA_SCOPE can be used to access different user
related data, like calendar, contacts, docs, etc.

OAuth2 works similar to OAuth but application must be defined on Google
APIs console https://code.google.com/apis/console/ Identity option.

OpenID also works straightforward, it doesn't need further configurations.
"""
from social.exceptions import AuthFailed
from social.backends.open_id import OpenIdAuth
from social.backends.oauth import BaseOAuth2, BaseOAuth1


class BaseGoogleAuth(object):
    def get_user_id(self, details, response):
        """Use google email as unique id"""
        email = validate_whitelists(self, details['email'])
        if self.setting('USE_UNIQUE_USER_ID', False):
            return response['id']
        else:
            return email

    def get_user_details(self, response):
        """Return user details from Orkut account"""
        email = response.get('email', '')
        return {'username': email.split('@', 1)[0],
                'email': email,
                'fullname': response.get('name', ''),
                'first_name': response.get('given_name', ''),
                'last_name': response.get('family_name', '')}


class GoogleOAuth2(BaseGoogleAuth, BaseOAuth2):
    """Google OAuth2 authentication backend"""
    name = 'google-oauth2'
    REDIRECT_STATE = False
    AUTHORIZATION_URL = 'https://accounts.google.com/o/oauth2/auth'
    ACCESS_TOKEN_URL = 'https://accounts.google.com/o/oauth2/token'
    ACCESS_TOKEN_METHOD = 'POST'
    DEFAULT_SCOPE = ['https://www.googleapis.com/auth/userinfo.email',
                     'https://www.googleapis.com/auth/userinfo.profile']
    EXTRA_DATA = [
        ('refresh_token', 'refresh_token', True),
        ('expires_in', 'expires'),
        ('token_type', 'token_type', True)
    ]

    def user_data(self, access_token, *args, **kwargs):
        """Return user data from Google API"""
        return self.get_json(
            'https://www.googleapis.com/oauth2/v1/userinfo',
            params={'access_token': access_token, 'alt': 'json'}
        )


class GoogleOAuth(BaseGoogleAuth, BaseOAuth1):
    """Google OAuth authorization mechanism"""
    name = 'google-oauth'
    AUTHORIZATION_URL = 'https://www.google.com/accounts/OAuthAuthorizeToken'
    REQUEST_TOKEN_URL = 'https://www.google.com/accounts/OAuthGetRequestToken'
    ACCESS_TOKEN_URL = 'https://www.google.com/accounts/OAuthGetAccessToken'
    DEFAULT_SCOPE = ['https://www.googleapis.com/auth/userinfo#email']

    def user_data(self, access_token, *args, **kwargs):
        """Return user data from Google API"""
        return self.get_querystring(
            'https://www.googleapis.com/userinfo/email',
            auth=self.oauth_auth(access_token)
        )

    def get_key_and_secret(self):
        """Return Google OAuth Consumer Key and Consumer Secret pair, uses
        anonymous by default, beware that this marks the application as not
        registered and a security badge is displayed on authorization page.
        http://code.google.com/apis/accounts/docs/OAuth_ref.html#SigningOAuth
        """
        key_secret = super(GoogleOAuth, self).get_key_and_secret()
        if key_secret == (None, None):
            key_secret = ('anonymous', 'anonymous')
        return key_secret


class GoogleOpenId(OpenIdAuth):
    name = 'google'
    URL = 'https://www.google.com/accounts/o8/id'

    def get_user_id(self, details, response):
        """
        Return user unique id provided by service. For google user email
        is unique enought to flag a single user. Email comes from schema:
        http://axschema.org/contact/email
        """
        return validate_whitelists(self, details['email'])


def validate_whitelists(backend, email):
    domain = email.split('@', 1)[1]
    emails = backend.setting('GOOGLE_WHITE_LISTED_EMAILS', [])
    domains = backend.setting('GOOGLE_WHITE_LISTED_DOMAINS', [])
    if (emails and email not in emails) or (domains and domain not in domains):
        raise AuthFailed(backend, 'Email or domain not allowed')
    return email
