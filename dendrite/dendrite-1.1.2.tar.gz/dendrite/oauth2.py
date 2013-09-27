from django.conf import settings 
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse, NoReverseMatch

import json, requests

try:
    from urllib import urlencode
    from urlparse import parse_qs 
except ImportError:
    from urllib.parse import parse_qs, urlencode
    


class OAuth2(object):
    def __init__(self, client_id=None, client_secret=None, 
                 authorization_url=None, access_token_url=None, redirect_uri=None,
                 requests=requests,
                 domain=None):

        assert client_id, "Please provide a `client_id` for this provider"
        assert client_secret, "Please provide a `client_secret` for this provider"

        assert authorization_url, "Please provide an `authorization_url` for this provider"
        assert authorization_url.startswith('https://'), "Please provide a SSL enabled `authorization_url` for this provider"

        assert access_token_url, "Please provide a `access_token_url` for this provider"
        assert access_token_url.startswith('https://'), "Please provide a SSL enabled `access_token_url` for this provider"

        assert redirect_uri, "Please provide a `redirect_uri` for this provider"

        self.client_id         = client_id
        self.client_secret     = client_secret

        self.authorization_url = authorization_url
        self.access_token_url  = access_token_url
        self._redirect_uri     = redirect_uri

        self.domain            = domain

        self.requests          = requests


    @property
    def redirect_uri(self):
        if self.domain is not None:
            domain = self.domain
        else:
            domain = Site.objects.get_current().domain

        # SSL by default. If you want to gamble on your security, feel
        # free to override this in your clients.
        try:
            return u'https://{}{}'.format(domain, reverse(self._redirect_uri))
        except NoReverseMatch:
            return u'https://{}{}'.format(domain, self._redirect_uri)

    def get_authorization_url(self, scope = '', **kwargs):
        params = {'client_id': self.client_id,
                  'redirect_uri': self.redirect_uri,
                  'scope': scope}
        
        params.update(kwargs)

        return u'{authorization_url}?{params}'.format(
            authorization_url=self.authorization_url,
            params=urlencode(params))


    def get_access_token(self, code, **kwargs):
        url = self.access_token_url

        data = {'code': code,
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'redirect_uri': self.redirect_uri}

        data.update(kwargs)

        response = self.requests.post(url, data=data)
        content = response.content

        try:
            return json.loads(content)
        except ValueError:
            return dict([(key, val[0]) for (key, val) in parse_qs(content).items()])
