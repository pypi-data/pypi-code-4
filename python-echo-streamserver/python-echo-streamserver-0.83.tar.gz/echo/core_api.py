""" Echo StreamServer Core API

This is the Core REST API for Echo StreamServer.

All API methods use this module, and can raise its echo.StreamServerError exception.
This indicates a server-side error, or malformed request.
"""

import urllib, urllib2
import base64

try:
    import json
except ImportError:
    import simplejson as json

import logging
from pprint import pformat

# Echo StreamServer Settings
# ======================================================================
from echo.settings import ECHO_HOST, ECHO_VERSION
from echo.settings import _ECHO_API_KEY, _ECHO_API_SECRET
if not (ECHO_HOST and ECHO_VERSION):
    raise ValueError("echo.settings: Undefined Echo HOST or VERSION code.")

# Use ECHO_TIMEOUT (seconds) unless there is an application-level timeout already.
import socket
if not socket.getdefaulttimeout():
    from echo.settings import ECHO_TIMEOUT
    try:
        socket.setdefaulttimeout(float(ECHO_TIMEOUT))
    except ValueError:
        _timeout_err_str = "Invalid ECHO_TIMEOUT %r must be an integer or float measured in seconds." % ECHO_TIMEOUT
        logging.error(_timeout_err_str)
        raise ValueError(_timeout_err_str)

#  Account Instance: (other than the default)
# ======================================================================
class Account(object):
    """ Echo StreamServer Account contains hidden API Key and hidden Secret. """
    BasicAuth = 'Basic'
    OAuth2 = '2-Legged OAuth2'

    def __init__(self, appkey, secret, auth_code):
        self._appkey = appkey
        self._secret = secret
        self._auth_code = auth_code

    def _get_auth_code(self):
        """ Returns auth type for this account. """
        if ECHO_OAUTH2 and (self._auth_code == self.OAuth2):
            return self.OAuth2
        else:
            return self.BasicAuth
    auth_code = property(_get_auth_code)

    def __str__(self):
        return "auth=%s key=[%s]" % (self._auth_code, self._appkey)

    def __repr__(self):
        return "(StreamServer Account[%s] %s)" % (self._auth_code, self._appkey)

default_login = Account.BasicAuth if '' == _ECHO_API_SECRET else Account.OAuth2
default_account = Account(_ECHO_API_KEY, _ECHO_API_SECRET, default_login)

# OAuth2 Header: Authenticate using 2-Legged OAuth.
# ======================================================================
# Use python-oauth2 libary to authenticate when available.
from oauth2_headers import get_oauth2_headers, ECHO_OAUTH2

def allowed_auth_types():
    """ Return the allowed authorization methods as a list of strings. """
    if ECHO_OAUTH2:
        return [ Account.BasicAuth, Account.OAuth2 ]
    else:
        return [ Account.BasicAuth ]

# Core HTTP Requests for any API Method
# ======================================================================
import sys
HTTP_HEADERS = {
    'User-Agent' : 'Echo/StreamServer API (Python %d.%d.%d)' % sys.version_info[:3],
}

class StreamServerError(Exception):
    """ The StreamServer API returns error reports for failed API methods.
    This exception wraps these server-side errors.
    Trap an echo.StreamServerError, e, and inspect its fields:
        e.errorCode: The Echo API code is a short string token.
        e.errorMessage: This is the long description.
    """
    def __init__(self, json_error):
        # {"result": "error", "errorCode": <errorCode>, "errorMessage": <errorMessage>}
        self.errorCode = json_error.get("errorCode", "none")
        self.errorMessage = json_error.get("errorMessage", None)
        Exception.__init__(self, "[%s] '%s'" % (self.errorCode, self.errorMessage))

def _auth_basic_request(request, account):
    """ Add "Authorization Basic" header to the current request.
    This is the less-secure alternative to OAuth.
    """
    base64string = base64.encodestring('%s:%s' % (account._appkey, account._secret)).replace('\n', '')
    request.add_header("Authorization", "Basic %s" % base64string)
    return request

class StreamServerRequest(urllib2.Request):
    """ ECHO StreamServer API HTTP Request objects pass an API method string, rather than a full URL.
    This should also handle the authentication rules.
    """
    def __init__(self, api_method='submit', data_dict={}, http_method='POST', headers=HTTP_HEADERS,
                 account=default_account, origin_req_host=None, unverifiable=False,
                 echo_host=ECHO_HOST, echo_version=ECHO_VERSION):
        self.data=urllib.urlencode(data_dict)
        post_data=None
        self.api_url = 'https://%s/%s/%s' % (echo_host, echo_version, api_method)
        if http_method == 'GET':
            self.api_url = "%s?%s" % (self.api_url, self.data)
            post_params=None
        else: # HTTP POST
            post_data=self.data
            post_params=data_dict
        urllib2.Request.__init__(self, self.api_url, data=post_data, headers=headers,
                                 origin_req_host=origin_req_host, unverifiable=unverifiable)

        # Add "Authorization" headers...
        if account.auth_code == Account.OAuth2:
            # Use python-oauth2 library to authenticate when available, and
            # requested.
            oauth2_d = get_oauth2_headers(account._appkey, account._secret,
                                          self.api_url, http_method,
                                          post_params=post_params)
            for k, v in oauth2_d.iteritems():
                self.add_header(k, v)
        else:
            # Otherwise, fallback to Authorization Basic.
            _auth_basic_request(self, account)

    def __unicode__(self):
        return "StreamServer API Request: %s" % (self.api_url)

# Send a raw HTTP request for an API Method.
# ======================================================================

def send_request(api_method, param_d={}, http_post=False, is_json=True,
                 account=default_account, echo_host=ECHO_HOST, echo_version=ECHO_HOST):
    """ Send a StreamServer API HTTP Request to ECHO.
    When is_json=True, the default, the document is parsed from JSON.
    The document is returned as a string when is_json=False.
    This is considered an internal function.
    """
    # Build api_method API request with param_d.
    result_doc = u''
    try:
        req = StreamServerRequest(api_method=api_method, data_dict=param_d,
                                  http_method=('POST' if http_post else 'GET'),
                                  account=account, echo_host=echo_host, echo_version=echo_version)
        logging.debug("%s API URL: %r" % (api_method, req.api_url))
        logging.debug("StreamServerRequest HTTP Headers:\n%s" % pformat(req.headers, indent=4))

        u = urllib2.urlopen(req)
        result_doc = u.read()
    except urllib2.HTTPError, e:
        # Py2.5- bug: Allow HTTP 201, etc to report.
        if e.code >= 400:
            logging.error("[HTTP %d] %s API Error" % (e.code, api_method))
        result_doc = e.read()
    except urllib2.URLError, e:
        logging.error("%s API Error: %s" % (api_method, str(e)))
        raise

    logging.debug("API Call Result:\n%s" % result_doc)

    # The document is returned as a string when is_json=False.
    if not is_json: return result_doc

    # When is_json=True, the document is parsed from JSON.
    try:
        result = json.loads(result_doc)
        # Handle result="error" JSON documents as exceptions.
        if 'result' in result and result['result'] == 'error':
            raise StreamServerError(result)
        return result
    except ValueError, e:
        logging.error("%s API JSON Error: %s" % (api_method, str(e)))
        error_json = {
                         'result': 'error',
                         'errorCode': 'bad_json_response',
                         'errorMessage': 'Invalid JSON Response',
                     }
        raise StreamServerError(error_json)

class EchoClient(object):
    """ Base EchoClient associates an Account with each API, e.g. Items API.
    A Client object is needed to use a non-default Account.
    """
    def __init__(self, account=default_account, echo_host=ECHO_HOST, echo_version=ECHO_VERSION):
        self._account = account
        self._echo_host = echo_host
        self._echo_version = echo_version

    _default_client = None
    @classmethod
    def get_client(cls):
        """ Get the default client object for this class.
        This is used by Echo API modules to expose methods.
        """
        if not cls._default_client:
            cls._default_client = cls()
        return cls._default_client

    def _send_request(self, api_method, param_d={}, http_post=False, is_json=True):
        """ Send a StreamServer API HTTP Request to ECHO for an API method name.
        When is_json=True, the default, the document is parsed from JSON.
        The document is returned as a string when is_json=False.
        This is an internal function to the client.
        """
        return send_request(api_method, param_d=param_d, http_post=http_post,
                            is_json=is_json, account=self._account, echo_host=self._echo_host,
                            echo_version=self._echo_version)

    def __str__(self):
        return "%s.%s: %s" % (self.__class__.__module__, self.__class__.__name__,
                              str(self._account))

    def __repr__(self):
        return str(self)

