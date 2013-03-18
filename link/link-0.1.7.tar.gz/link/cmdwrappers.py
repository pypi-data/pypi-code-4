"""
apilink contains all of the classes that you need to connect to a configured
api.  It wraps the python requests package, and provides some helpful functions
that make it easy to parse json and xml responses
"""

import sys
import requests
from requests.auth import HTTPBasicAuth
from functools import wraps
import json
from xml.etree import cElementTree as ET
from link import Wrapper

class ShCmderResponse(object):
    """
    Wraps the response of a shell command
    """
    
    def __init__(self, wrap_name=None, output):
        self.output = output
        super(CmdResponse, self).__init__(wrap_name)

    def json(self):
        return json.loads(self.output)

    def split(self, seperator = " "):
        return self.output.split(seperator)


class ShCmder(object):
    """
    Wrap an API response and make it easy to parse out
    json or XML
    """
    def __init__(self, cmds):
        pass

    def run(self, 

    def __call__(self, params = None):

        if not params:
            params = {}

    

class APIResponseWrapper(Wrapper):
    """
    Wrap an API response and make it easy to parse out
    json or XML
    """
    def __init__(self, wrap_name = None, response = None):
        self._json = None
        self._xml = None
        super(APIResponseWrapper, self).__init__(wrap_name, response)

    @property
    def json(self):
        """
        json's the content and returns it as a dictionary
        """
        if not self._json:
            try:
                self._json = json.loads(self.content)
            except:
                raise ValueError("Response is not valid json %s " % self.content)
        return self._json

    @property
    def xml(self):
        """
        json's the content and returns it as a dictionary
        """
        if not self._xml:
            try:
                self._xml = ET.XML(self.content)
            except:
                raise ValueError("Response is not valid xml %s " % self.content)
        return self._xml

    @property
    def error(self):
        """
        Returns the wrappers error by default but can be overridden 
        """
        return self._wrapped.error
 
    def tostring(self):
        """
        If you have parsed json or xml it will
        return the manipulated object as a string.  Might not be a very helpful
        function
        """
        if self._json:
            return json.dumps(self._json)

        if self._xml:
            return ET.tostring(self._xml)

    def noauth(self):
        """
        """
        pass

class APIRequestWrapper(Wrapper):
    """
    Wraps the requests class so that all you have to give is
    extra url parameters for it to work fine
    """
    requests = requests
    headers = {'Accept': '*/*',
                        'Accept-Encoding': 'identity, deflate, compress, gzip',
                        'User-Agent': 'Mozilla/5.0'
                      }

    def __init__(self, wrap_name=None, base_url=None, user=None, password=None, 
                response_wrapper = APIResponseWrapper ):
        self.base_url = base_url
        self.user = user
        self.password = password
        self.response_wrapper = response_wrapper 
        sess = requests.session(headers = self.headers)
        super(APIRequestWrapper, self).__init__(wrap_name, sess)
        sess.auth = self.authenticate() 
    
    def authenticate(self):
        """
        The authenicate function is called in the init of APIRequestWrapper.  
        This can be overridden for customized Authentication.  By Default
        it will auth using HTTPBasicAuth
        """
        if self.user and self.password:
            return HTTPBasicAuth(self.user, self.password)

    def request(self, method='get', url_params = '' , data = '', allow_reauth =
                True, **kwargs):
        """
        Make a request.  This is taken care af by the request decorator
        """
        if isinstance(url_params, dict):
            #tricky, if its a dictonary turn it into a & delimited key=value
            url_params = '&'.join([ '%s=%s' % (key, value) for key,value
                                   in url_params.items()])

        full_url = self.base_url + url_params
        #turn the string method into a function name
        method = self._wrapped.__getattribute__(method)
        resp = self.response_wrapper(response = method(full_url, data = data, 
                                                       **kwargs))
        #if you get a no auth then retry the auth
        if allow_reauth and resp.noauth():
            self.authenicate()
            self.request(method, url_params, data, allow_reauth=False, **kwargs)

        return resp
    
    def get(self, url_params = '', **kwargs):
        """
        Make a get call
        """
        return self.request('get', url_params = url_params, **kwargs)

    def put(self, url_params='', data='', **kwargs):
        """
        Make a put call
        """
        return self.request('put', url_params = url_params, data = data,
                            **kwargs)

    def post(self, url_params='', data='', **kwargs):
        """
        Make a post call
        """
        return self.request('post', url_params = url_params, data = data,
                            **kwargs)

    def clear_session(self):
        """
        clears the session and reauths
        """
        sess = requests.session(headers = self.headers)
        self._wrapped = sess
        self._wrapped = self.authenticate()
