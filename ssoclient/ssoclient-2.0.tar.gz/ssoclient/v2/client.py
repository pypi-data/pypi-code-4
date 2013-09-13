# Copyright 2013 Canonical Ltd. This software is licensed under
# the GNU Affero General Public License version 3 (see the file
# LICENSE).
from datetime import datetime

from requests_oauthlib import OAuth1

from ssoclient.v2.http import ApiSession
from ssoclient.v2 import errors


def datetime_from_string(value):
    """Parse a string value representing a date in isoformat."""
    try:
        result = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%f')
    except ValueError:
        result = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')
    return result


def parse_datetimes(value):
    """Recursively look for dates and try to parse them into datetimes."""
    assert isinstance(value, dict)
    result = value.copy()
    for k, v in value.iteritems():
        if isinstance(v, dict):
            result[k] = parse_datetimes(v)
        elif isinstance(v, list):
            result[k] = [parse_datetimes(i) for i in v]
        elif 'date' in k:
            result[k] = datetime_from_string(v)
    return result


class V2ApiClient(object):
    """High-level client for theV2.0 API SSO resources."""

    def __init__(self, endpoint):
        self.session = ApiSession(endpoint)

    def _unicode_credentials(self, credentials):
        # if openid and credentials come directly from a call to client.login
        # then whether they are unicode or byte-strings depends on which
        # json library is in use.
        # oauthlib requires them to be unicode - so we coerce to be sure.
        if credentials is not None:
            consumer_key = unicode(credentials.get('consumer_key', ''))
            consumer_secret = unicode(credentials.get('consumer_secret', ''))
            token_key = unicode(credentials.get('token_key', ''))
            token_secret = unicode(credentials.get('token_secret', ''))
            oauth = OAuth1(
                consumer_key,
                consumer_secret,
                token_key, token_secret,
            )
        else:
            oauth = None
        return oauth

    def _merge(self, data, extra):
        """Allow data to passed to functions by keyword or by dict."""
        if data:
            data.update(extra)
        else:
            data = extra
        return data

    def register(self, data=None, **kwargs):
        response = self.session.post(
            '/accounts', data=self._merge(data, kwargs))
        result = parse_datetimes(response.content)
        return result

    def login(self, data=None, **kwargs):
        response = self.session.post(
            '/tokens/oauth', data=self._merge(data, kwargs))
        result = parse_datetimes(response.content)
        return result

    def account_details(self, openid, token=None, expand=False):
        openid = unicode(openid)
        oauth = self._unicode_credentials(token)
        url = '/accounts/%s?expand=%s' % (openid, str(expand).lower())

        response = self.session.get(url, auth=oauth)
        result = parse_datetimes(response.content)
        return result

    def email_delete(self, email, credentials):
        oauth = self._unicode_credentials(credentials)
        response = self.session.delete('/emails/%s' % email, auth=oauth)
        return response.status_code == 204

    def email_details(self, email, credentials):
        oauth = self._unicode_credentials(credentials)

        response = self.session.get('/emails/%s' % email, auth=oauth)
        result = parse_datetimes(response.content)
        return result

    def token_delete(self, token_key, credentials):
        oauth = self._unicode_credentials(credentials)
        response = self.session.delete(
            '/tokens/oauth/%s' % token_key, auth=oauth)
        return response.status_code == 204

    def token_details(self, token_key, credentials):
        oauth = self._unicode_credentials(credentials)

        response = self.session.get('/tokens/oauth/%s' % token_key, auth=oauth)
        result = parse_datetimes(response.content)
        return result

    def validate_request(self, data=None, **kwargs):
        response = self.session.post(
            '/requests/validate', data=self._merge(data, kwargs))
        return response.content

    def request_password_reset(self, email, token=None):
        response = self.session.post(
            '/tokens/password', data=dict(email=email, token=token))
        return response.content
