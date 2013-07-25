import requests
from version import VERSION

try:
    import simplejson as json
except ImportError:
    import json


__apikey__ = ''
url = 'https://attendly.me/api/v4'
response = ''
request_id = 1
error_code = None
error_message = None

def apikey(key):
    global __apikey__
    __apikey__ = key


class User(object):
    def __init__(self):
        self.prefix = 'user'

    @classmethod
    def login(self, name, password):
        params = {'user' : {'name': name, 'password': password}}
        result = call('user.login', params)
        return result['user']

    @classmethod
    def get(self, id):
        params = {'user' : {'id': id}}
        result = call('user.get', params)
        return result['user']


class Event(object):
    def __init__(self):
        self.prefix = 'event'

    @classmethod
    def get(self, id):
        params = {'event' : {'id': id}}
        result = call('event.get', params)
        return result['event']

    @classmethod
    def list(self):
        params = {}
        result = call('event.list', params)
        return result

def call(method, params):
    global __apikey__

    h = {'content-type': 'application/json', 'client': 'python'+VERSION}
    d = {"jsonrpc": "2.0", "method": method, "params": params, "id": request_id}
    r = requests.post(url, data=json.dumps(d), auth=(__apikey__, ''), headers=h)
    response = json.loads(r.text)

    # We need to check for an error
    if 'error' in response:
        error_code = response['error']['code']
        error_message = response['error']['message']
        raise AttendlyError(error_code, error_message)

    return response['result']


class AttendlyError(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __str__(self):
        return repr(self.message)
