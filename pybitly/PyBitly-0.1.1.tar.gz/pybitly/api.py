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

    def _open_url(self, url=None, data=None, headers=dict()):
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

    def _check_if_list(self, param=None):
        return not isinstance(param, basestring) and isinstance(param, list)

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

    def shorten(self, urls=None, domain=None):
        return_list, short_url_list, params = self._check_if_list(urls), [], dict()

        params['access_token'] = self.access_token
        if not domain is None:
            params['domain'] = domain

        if return_list:
            for url in urls:
                params['longUrl'] = url
                response_data = self._open_url(API_SHORTEN_URL + "?" + urllib.urlencode(params))
                json_data = simplejson.loads(response_data.read())

                if json_data['data']:
                    short_url_list.append(json_data['data']['url'])
                else:
                    short_url_list.append(json_data['status_txt'])
        else:
            params['longUrl'] = urls
            response_data = self._open_url(API_SHORTEN_URL + "?" + urllib.urlencode(params))
            json_data = simplejson.loads(response_data.read())

            if json_data['data']:
                short_url_list.append(json_data['data']['url'])
            else:
                short_url_list.append(json_data['status_txt'])

        if return_list:
            return short_url_list

        return short_url_list[0]

    def expand(self, urls=None):
        return_list, params, long_url_list = self._check_if_list(urls), '', []

        if return_list:
            for url in urls:
                params += urllib.urlencode({'shortUrl': url}) + '&'
        else:
            params += urllib.urlencode({'shortUrl': urls}) + '&'

        params += urllib.urlencode({'access_token': self.access_token})
        response_data = self._open_url(API_EXPAND_URL + "?" + params)
        json_data = simplejson.loads(response_data.read())

        if len(json_data['data']):
            for exp in json_data['data']['expand']:
                errors = exp.get('error', None)
                if errors:
                    long_url_list.append(errors)
                else:
                    long_url_list.append(exp.get('long_url'))
        else:
            long_url_list.append(json_data['status_txt'])

        if not return_list:
            return long_url_list[0]

        return long_url_list