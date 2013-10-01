import urllib2
import urllib
import base64

try:
    import simplejson
except ImportError:
    import json as simplejson

API_URL="https://api-ssl.bitly.com/oauth/access_token"
API_SHORTEN_URL="https://api-ssl.bitly.com/v3/shorten"
API_EXPAND_URL="https://api-ssl.bitly.com/v3/expand"

class ApiException(Exception):

    """
    Class for raising Bitly Api exceptions.
    """
    pass

class Api(object):

    """
    Pass your login and password to obtain API key
    """
    def __init__(self, login=None, password=None):
        self.login = login
        self.password = password

        if self.login is None or self.password is None:
            raise ApiException("You need to pass your login and password.")

        self.access_token = self.get_access_token()

    def _open_url(self, url, data=None, headers={}):
        request = urllib2.Request(url, data, headers)
        try:
            response = urllib2.urlopen(request)
        except urllib2.URLError as error:
            if hasattr(error, 'reason'):
                raise ApiException("Failed to reach server. Reason: %s" % error.reason)
            elif hasattr(error, 'code'):
                raise ApiException("Server error. Wrong request: %s" % error.code)
        else:
            return response

    def get_access_token(self):
        auth_data = {
            'client_secret': self.password,
            'client_id': self.login
        }
        auth_encoded = base64.b64encode(self.login + ':' + self.password)
        headers = {
            'Authorization': 'Basic ' + auth_encoded
        }

        response_data = self._open_url(API_URL, simplejson.dumps(auth_data), headers)
        return response_data.read()

    def shorten(self, urls, domain=None):
        params = {
            'access_token': self.access_token,
            'longUrl': urls
        }
        if not domain is None:
            params['domain'] = domain

        response_data = self._open_url(API_SHORTEN_URL + "?" + urllib.urlencode(params))

        json_data = simplejson.loads(response_data.read())

        if json_data['data']:
            return json_data['data']['url']

        return json_data['status_txt']

    def expand(self, urls):
        return_list, params = False, ''
        if not isinstance(urls, basestring) and isinstance(urls, list):
            return_list = True
            for url in urls:
                params += urllib.urlencode({'shortUrl': url}) + '&'
        else:
            params += urllib.urlencode({'shortUrl': urls}) + '&'

        params += urllib.urlencode({'access_token': self.access_token})

        response_data = self._open_url(API_EXPAND_URL + "?" + params)

        json_data = simplejson.loads(response_data.read())
        long_url_list = []

        for exp in json_data['data']['expand']:
            errors = exp.get('error', None)
            if errors:
                long_url_list.append(errors)
            else:
                long_url_list.append(exp.get('long_url'))

        if not return_list:
            return long_url_list[0]

        return long_url_list