"""
OAuth2.0a 'Bearer Token' handling.
Based on https://github.com/OfflineLabs/python-oauth2/
  * rips out all the httplib2 stuff
  * rips out all the OAuth1.0a stuff
  * based on the newest version of the spec[1] instead of the initial version

[1] http://tools.ietf.org/html/draft-ietf-oauth-v2-18
    http://tools.ietf.org/html/draft-ietf-oauth-v2-bearer-06

The MIT License

Portions Copyright (c) 2011 Jack Diederich c/o Curata, Inc.
Portions Copyright (c) 2007 Leah Culver, Joe Stump, Mark Paschal, Vic Fryzel

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import urllib
import urllib2
import StringIO

try:
    import simplejson
except ImportError:
    # Have django or are running in the Google App Engine?
    from django.utils import simplejson

VERSION = '1.1'

class Error(RuntimeError):
    """Generic exception class."""

    def __init__(self, message='OAuth error occured.'):
        self._message = message

    @property
    def message(self):
        """A hack to get around the deprecation errors in 2.6."""
        return self._message

    def __str__(self):
        return self._message

class Client(object):
    """ Client for OAuth 2.0 'Bearer Token' """
    redirect_uri = None
    auth_uri = None
    refresh_uri = None
    user_agent = None
    scope = None

    def __init__(self, client_id, client_secret, access_token=None,
                 refresh_token=None, timeout=None):
        if not client_id or not client_secret:
            raise ValueError("Client_id and client_secret must be set.")
        self.client_id = client_id
        self.client_secret = client_secret
        self.timeout = timeout
        self.access_token = access_token
        self.refresh_token = refresh_token
        self._authorization_redirect_uri = None

    def authorization_url(self, auth_uri=None, redirect_uri=None, scope=None, state=None,
                          access_type='offline', approval_prompt=None):
        """ Get the URL to redirect the user for client authorization """
        if redirect_uri is None:
            redirect_uri = self.redirect_uri
        if redirect_uri:
            self._authorization_redirect_uri = redirect_uri
        if auth_uri is None:
            auth_uri = self.auth_uri
        if not auth_uri:
            raise ValueError("an auth_uri is required")
        if scope is None:
            scope = self.scope

        params = {'client_id' : self.client_id,
                  'redirect_uri' : redirect_uri,
                  'response_type' : 'code',
                 }
        if scope:
            params['scope'] = scope

        if state:
            params['state'] = state

        if access_type:
            # 'offline' requests get a refresh_token too
            params['access_type'] = access_type

        if approval_prompt:
            params['approval_prompt'] = approval_prompt

        return '%s?%s' % (auth_uri, urllib.urlencode(params))

    def redeem_code(self, refresh_uri=None, redirect_uri=None, code=None, scope=None):
        """Get an access token from the supplied code """
        if code is None:
            raise ValueError("Code must be set. see see http://tools.ietf.org/html/draft-ietf-oauth-v2-20#section-4.1.3")
        if redirect_uri is None:
            redirect_uri = self.redirect_uri
        if self._authorization_redirect_uri and redirect_uri != self._authorization_redirect_uri:
            raise ValueError("redirect_uri mismatch. see http://tools.ietf.org/html/draft-ietf-oauth-v2-20#section-4.1.3")
        if refresh_uri is None:
            refresh_uri = self.refresh_uri
        if scope is None:
            scope = self.scope

        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'grant_type' : 'authorization_code',
        }
        if redirect_uri is not None:
            data['redirect_uri'] = redirect_uri
        if scope is not None:
            data['scope'] = scope
        body = urllib.urlencode(data)

        headers = {'Content-type' : 'application/x-www-form-urlencoded'}
        if self.user_agent:
            headers['user-agent'] = self.user_agent

        response = self._request(refresh_uri, body=body, method='POST', headers=headers)

        if response.code != 200:
            raise Error(response.read())
        response_args = simplejson.loads(response.read())
        error = response_args.pop('error', None)
        if error is not None:
            raise Error(error)

        self.access_token = response_args['access_token']
        # refresh token is optional
        self.refresh_token = response_args.get('refresh_token', '')
        return self.access_token, self.refresh_token

    def refresh_access_token(self, refresh_uri=None, refresh_token=None, grant_type='refresh_token'):
        """  Get a new access token from the supplied refresh token """

        if refresh_uri is None:
            refresh_uri = self.refresh_uri
        if refresh_token is None:
            refresh_token = self.refresh_token

        # prepare required args
        args = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': refresh_token,
            'grant_type' : grant_type,
        }
        body = urllib.urlencode(args)

        headers = {'Content-type' : 'application/x-www-form-urlencoded'}
        if self.user_agent:
            headers['user-agent'] = self.user_agent

        response = self._request(refresh_uri, method='POST', body=body, headers=headers)
        if response.code != 200:
            raise Error(response.read())
        response_args = simplejson.loads(response.read())

        self.access_token = response_args['access_token']
        # server may or may not supply a new refresh token
        self.refresh_token = response_args.get('refresh_token', self.refresh_token)
        return self.access_token, self.refresh_token

    def _request(self, uri, body=None, headers=None, method='GET'):
        if method == 'POST' and not body:
            raise ValueError('POST requests must have a body')

        request = urllib2.Request(uri, body, headers)
        try:
            return urllib2.urlopen(request, timeout=self.timeout)
        except urllib2.HTTPError as e:
            e.body = e.read()
            e.fp = StringIO.StringIO(e.body)
            e.read = e.fp.read
            if e.body:
                e.msg += ' %r' % e.body
            raise

    def request(self, uri, body, headers, method='GET'):
        """ perform a HTTP request using OAuth authentication.
            If the request fails because the access token is expired it will
            try to refresh the token and try the request again.
        """
        headers['Authorization'] = 'Bearer %s' % self.access_token

        try:
            response = self._request(uri, body=body, headers=headers, method=method)
        except urllib2.HTTPError as e:
            if e.code == 403 and 'rate' in e.body.lower() and 'limit' in e.body.lower():
                self.handle_rate_limit()
                response = self._request(uri, body=body, headers=headers, method=method)
            elif 400 <= e.code < 500 and e.code != 404:
                # any 400 code is acceptable to signal that the access token is expired.
                self.refresh_access_token()
                headers['Authorization'] = 'Bearer %s' % self.access_token
                response = self._request(uri, body=body, headers=headers, method=method)
            else:
                raise

        if response.code == 200:
            body = response.read()
            return simplejson.loads(body)
        raise ValueError(response.read())

    def handle_rate_limit(self):
        import random
        import time
        time.sleep(1 + random.random() * 3)


class GooglAPI(Client):
    user_agent = 'python-foauth2'
    # OAuth API
    auth_uri = 'https://accounts.google.com/o/oauth2/auth'
    refresh_uri = 'https://accounts.google.com/o/oauth2/token'
    scope = 'https://www.googleapis.com/auth/urlshortener'
    # data API
    api_uri = 'https://www.googleapis.com/urlshortener/v1/url'

    def shorten(self, long_url):
        data = simplejson.dumps({'longUrl' : long_url})
        headers = {'Content-Type': 'application/json'}
        json_d = self.request(self.api_uri, data, headers, 'POST')
        return json_d['id']

    def stats(self, short_url):
        params = {'shortUrl': short_url,
                  'projection' : 'ANALYTICS_CLICKS',
                 }
        stat_url = self.api_uri + '&' + urllib.urlencode(params)
        headers = {'Content-Type': 'application/json'}
        return self.request(stat_url, None, headers)


class BufferAPI(GooglAPI):
    auth_uri = 'https://bufferapp.com/oauth2/authorize'
    refresh_uri = 'https://api.bufferapp.com/1/oauth2/token.json'
    scope = None
    service = 'buffer'
    data_uri = 'https://api.bufferapp.com/1/'

    def authorization_url(self, **kwargs):
        # Buffer doesn't use access_type
        kwargs['access_type'] = None
        return super(BufferAPI, self).authorization_url(**kwargs)

    def get_profiles(self):
        url = self.data_uri + 'profiles.json'
        headers = {'Content-Type' : 'application/json'}
        return self.request(url, None, headers)

    def get_info(self):
        url = self.data_uri + 'info/configuration.json'
        headers = {'Content-Type' : 'application/json'}
        return self.request(url, None, headers)

    def get_pending(self, profile_id):
        url = self.data_uri + 'profiles/%s/updates/pending.json' % profile_id
        headers = {'Content-Type' : 'application/json'}
        return self.request(url, None, headers)

    def post_update(self, profile_ids, message):
        url = self.data_uri + 'updates/create.json'
        import urllib
        data = [('text', urllib.urlencode(message)), ('shorten', 1)]
        for pid in profile_ids:
            data.append(('profile_ids[]', pid))
        body = urllib.urlencode(data)
        headers = {'Content-type' : 'application/x-www-form-urlencoded'}
        return self.request(url, body, headers)


class GAnalyticsAPI(GooglAPI):
    # OAuth API
    refresh_uri = 'https://accounts.google.com/o/oauth2/token'
    scope = 'https://www.googleapis.com/auth/analytics.readonly'
    service = 'ganalytics'

    # data API
    def lookup_table_id(self, ga_id):
        """ Find the table_id for the given analytics id """
        ua, first, second = ga_id.split('-')
        url = 'https://www.googleapis.com/analytics/v3/management/accounts/%s/webproperties/UA-%s-%s/profiles'
        url = url % (first, first, second)
        headers = {'Content-Type' : 'application/json'}
        data = self.request(url, None, headers)
        return 'ga:' + data['items'][0]['id']

    def feed_query(self, params):
        url = 'https://www.googleapis.com/analytics/v3/data/ga'
        headers = {'Content-Type' : 'application/json'}
        return self.request('%s?%s' % (url, urllib.urlencode(params)), None, headers)


class GoogleSMAPI(Client):
    user_agent = 'python-foauth2'
    # OAuth API
    auth_uri = 'https://accounts.google.com/o/oauth2/auth'
    refresh_uri = 'https://accounts.google.com/o/oauth2/token'
    scope = 'https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.email'

    # data API
    userinfo_uri = "https://www.googleapis.com/oauth2/v1/userinfo"
    search_uri = "https://www.googleapis.com/plus/v1/activities"
    list_uri = "https://www.googleapis.com/plus/v1/people/%s/activities/public"

    def account_name(self):
        url = "%s?%s" % (self.userinfo_uri, urllib.urlencode({"access_token":self.access_token}))
        headers = {'Content-Type': 'application/json'}
        data = self.request(url, None, headers)
        return data.get("email", "Name Unavailable")

    def search(self, query, count):
        url = "%s?%s" % (self.search_uri,
                         urllib.urlencode({"query":query, "maxResults":count, "orderBy":"recent"}))
        headers = {'Content-Type': 'application/json'}
        data = self.request(url, None, headers)
        return data

    def list(self, uid, count):
        url = "%s?%s" % (self.list_uri % uid,
                         urllib.urlencode({"maxResults":count}))
        headers = {'Content-Type': 'application/json'}
        data = self.request(url, None, headers)
        return data
