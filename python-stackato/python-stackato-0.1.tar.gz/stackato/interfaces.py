import json
import urllib
from urlparse import urljoin
import requests
from stackato.exceptions import StackatoException, StackatoAuthenticationException
import os

'''
Represents an interface to communicate with a
Stackato micro cloud or cluster (known as a Stackato instance).
'''
class StackatoInterface(object):
    
    TOKEN_FILE_LOCAL_PATH = '~/.stackato/client/token'

    '''
    Initializes the interface. This interface
    allows developers to make calls to the Stackato API.
    '''
    def __init__(self, target, username=None, password=None, store_token=False):
        self.target = target                # the Stackato instance we are targeting
        self.username = username            # username used to log into the instance
        self.password = password            # password used for the username
        self.token = None                   # token that is required for authenticated calls to the API
        self.store_token = store_token      # flag to store the token locally on the computer
        self.token_file = os.path.expanduser(self.TOKEN_FILE_LOCAL_PATH)    # path to the file that contains the token

        # check if the token is currently within the file. if it is, extract it and set self.token
        if self.store_token:
            if os.path.exists(self.token_file):
                with open(self.token_file) as fobj:
                    try:
                        data = json.load(fobj)
                        if self.target in data:
                            self.token = data[self.target]
                    except ValueError: # Invalid JSON in file, probably empty (or modified. Kids these days...)
                        pass

    '''
    Retrieves the "Authentication:" header required for making specific calls to the
    Stackato Client API.
    '''
    def get_auth_args(self, authentication_required):
        if not (authentication_required or self.token):
            return {}
        elif not self.token and self.store_token: # Ignore, will request new token afterwards!
            return {}
        elif not self.token:
            raise StackatoAuthenticationException("Please login before using this function.")
        return {'Authorization': self.token}

    '''
    Make a generic request to the Stackato API.

    If no data is specified, the request to the specified
    URL assumes that this is a GET request, with no authentication
    token required.
    '''
    def _request(self, url, request_type=requests.get, authentication_required=True, data=None):
        if data:
            data = json.dumps(data)
        request = request_type(urljoin(self.target, url), data=data, headers=self.get_auth_args(authentication_required), verify=False)
        if request.status_code == 200:
            return request
        elif request.status_code == 403:
            if not authentication_required:
                raise StackatoAuthenticationException(request.text)
            else:
                self.login()
                return self._request(url, request_type, authentication_required=False, data=data)
        elif request.status_code == 404:
            raise StackatoException("HTTP %s - %s" % (request.status_code, request.text))
        else:
            raise StackatoException("HTTP %s - %s" % (request.status_code, request.text))

    '''
    Attempt to make the request. If it completes without errors,
    return the JSON object returned by the request.
    '''
    def _get_json_or_exception(self, *args, **kwargs):
        return self._request(*args, **kwargs).json()

    '''
    Attempt to make the request. If it completes without errors,
    return true.
    '''
    def _get_true_or_exception(self, *args, **kwargs):
        self._request(*args, **kwargs)
        return True

    '''
    Attempt to login to the Stackato instance. Also
    sets self.token for the authenticted user.
    '''
    def login(self):
        self.token = self._get_json_or_exception(
            "users/%s/tokens" % urllib.quote_plus(self.username),
            request_type=requests.post,
            authentication_required=False,
            data={'password': self.password}
        )['token']
        if self.store_token:
            data = {self.target: self.token}
            if os.path.exists(self.token_file):
                try:
                    with open(self.token_file) as token_file:
                        data = json.loads(token_file.read())
                        data[self.target] = self.token
                except ValueError: # Invalid JSON in file, probably empty
                    pass
            with open(self.token_file, 'w') as token_file:
                json.dump(data, token_file)
        return True

    '''
    Generic GET request to the Stackato API.
    '''
    def _get(self, url):
        return self._get_json_or_exception(url)

    '''
    Generic POST request to the Stackato API.
    '''
    def _post(self, url, data):
        return self._get_json_or_exception(url, request_type=requests.post, data=data)

    '''
    Generic PUT request to the Stackato API.
    '''
    def _put(self, url, data):
        return self._get_true_or_exception(url, request_type=requests.put, data=data)

    '''
    Generic DELETE request to the Stackato API.
    '''
    def _delete(self, url):
        return self._get_true_or_exception(url, request_type=requests.delete)

    def get_apps(self):
        return self._get('apps')

    def get_app(self, name):
        return self._get('apps/%s' % name)

    def put_app(self, name, data):
        return self._put(("apps/%s" % name), data)

    def delete_app(self, name):
        return self._delete("apps/%s" % name)

    def get_app_crashes(self, name):
        return self._get("apps/%s/crashes" % name)

    def get_app_instances(self, name):
        return self._get("apps/%s/instances" % name)

    def get_app_stats(self, name):
        return self._get("apps/%s/stats" % name)

    def get_services(self):
        return self._get("services/")

    def get_service(self, name):
        return self._get("services/%s" % name)

    def delete_service(self, name):
        return self._delete("services/%s" % name)
