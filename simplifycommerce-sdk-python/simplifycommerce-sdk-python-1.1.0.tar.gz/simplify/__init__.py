
#
# Copyright (c) 2013, MasterCard International Incorporated
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without modification, are 
# permitted provided that the following conditions are met:
# 
# Redistributions of source code must retain the above copyright notice, this list of 
# conditions and the following disclaimer.
# Redistributions in binary form must reproduce the above copyright notice, this list of 
# conditions and the following disclaimer in the documentation and/or other materials 
# provided with the distribution.
# Neither the name of the MasterCard International Incorporated nor the names of its 
# contributors may be used to endorse or promote products derived from this software 
# without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY 
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES 
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT 
# SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, 
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; 
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER 
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING 
# IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF 
# SUCH DAMAGE.
#


from urllib2 import Request, urlopen, quote, URLError, HTTPError
import sys
import base64
import json
import hmac
import hashlib
import time
import random


from simplify.constants import Constants
from simplify.domain import DomainFactory, Domain

################################################################################
# Constants
################################################################################

HTTP_SUCCESS = 200
HTTP_REDIRECTED = 302
HTTP_UNAUTHORIZED = 401
HTTP_NOT_FOUND = 404
HTTP_NOT_ALLOWED = 405
HTTP_BAD_REQUEST = 400

HTTP_METHOD_POST = "POST"
HTTP_METHOD_PUT = "PUT"
HTTP_METHOD_GET = "GET"
HTTP_METHOD_DELETE = "DELETE"


################################################################################
# Global variables
################################################################################


public_key = None
private_key = None
api_base_sandbox_url = Constants.api_base_sandbox_url
api_base_live_url = Constants.api_base_live_url
oauth_base_url = Constants.oauth_base_url
user_agent = None


################################################################################
# Utilities
################################################################################

def build_query_string(criteria):

    if criteria == None:
        return ''

    query_string = []
    if 'max' in criteria:
        query_string.append("max=" + str(criteria['max']))

    if 'offset' in criteria:
        query_string.append("offset=" + str(criteria['offset']))

    if 'sorting' in criteria:
        for key, value in criteria['sorting'].iteritems():
            query_string.append("sorting[" + key + "]=" + quote(str(value)))

    if 'filter' in criteria:
        for key, value in criteria['filter'].iteritems():
            query_string.append("filter[" + key + "]=" + quote(str(value)))

    return '&'.join(query_string)

def handle_http_error(response_body, response_code):

    if response_code == HTTP_REDIRECTED:  # this shouldn't happen - if it does it's our problem
        raise BadRequestError("Unexpected response code returned from the API, have you got the correct URL?", response_code, response_body)
    elif response_code == HTTP_BAD_REQUEST:
        raise BadRequestError("Bad request", response_code, response_body)

    elif response_code == HTTP_UNAUTHORIZED:
        raise AuthenticationError("You are not authorized to make this request.  Are you using the correct API keys?", response_code, response_body)

    elif response_code == HTTP_NOT_FOUND:
        raise ObjectNotFoundError("Object not found", response_code, response_body)

    elif response_code == HTTP_NOT_ALLOWED:
        raise NotAllowedError("Operation not allowed", response_code, response_body)

    elif response_code < 500:
        raise BadRequestError("Bad request", response_code, response_body)

    else:
        raise SysError("An unexpected error has been raised.  Looks like there's something wrong at our end." , response_code, response_body)


################################################################################
# Authentication
################################################################################

class Authentication:

    """
        Holds authentication information used when accessing the API.

        @ivar public_key: Public key used to access the API.
        @ivar private_key: Private key used to access the API.
        @ivar access_token: OAuth token used to access the API.
    """

    def __init__(self, **kwargs):
        """
            Constructs an Authentication object.

            @param kwargs: contains initial values for the instance variables.  Valid keywords
                   are public_key, private_key and access_token.  If no value is passed for
                   public_key or its value is None then simplify.public_key is used.  If no
                   value is passed for private_key or its value is None then simplify.private_key
                   is used.
            @return: an Authentication object
        """

        self.public_key = kwargs['public_key'] if 'public_key' in kwargs else None
        if self.public_key == None:
            global public_key
            self.public_key = public_key

        self.private_key = kwargs['private_key'] if 'private_key' in kwargs else None
        if self.private_key == None:
            global private_key
            self.private_key = private_key

        self.access_token = kwargs['access_token'] if 'access_token' in kwargs else None


class AccessToken(Domain):
    """
        OAuth access token.

        @ivar access_token: Access token used when making an API call authenticated using OAuth
        @ivar refresh_token: Token used when refreshing an access token.
        @ivar expires_in: Number of seconds from the time the token was created till it expires.
    """

    @staticmethod
    def create(auth_code, redirect_uri, *auth_args):
        """
          Creates an AccessToken object.

          @param auth_codes: OAuth authentication code.
          @param redirect_uri: URI to which OAuth requests are redirected.
          @param auth_args: an Authentication object used for the API call.  If no value is passed the gloabl keys simplify.public_key and simplify.private_key are used.
          @return: an AccessToken object object
        """

        props = {
            'grant_type' : 'authorization_code',
            'code' : auth_code,
            'redirect_uri' : redirect_uri
        }

        h = PaymentsApi().send_auth_request(props, 'token', PaymentsApi.create_auth_object(auth_args))
        return AccessToken(h)


    def refresh(self, *auth_args):
        """
          Refreshes an AccessToken object.  If successful the access_token, refresh_token and expires_in attributes are updated.

          @param auth_args: an Authentication object used for the API call.  If no value is passed the global keys simplify.public_key and simplify.private_key are used.
        """

        rt = self['refresh_token']
        if not rt:
            raise IllegalArgumentError("Cannot refresh access token; refresh token is invalid.")

        props = {
            'grant_type' : 'refresh_token',
            'refresh_token' : rt
        }

        h = PaymentsApi().send_auth_request(props, 'token', PaymentsApi.create_auth_object(auth_args))
        self.__dict__.update(h)


    def revoke(self, *auth_args):
        """
          Revokes an AccessToken object.

          @param auth_args: an Authentication object used for the API call.  If no value is passed the global keys simplify.public_key and simplify.private_key are used.
        """

        token = self['access_token']
        if not token:
            raise IllegalArgumentError("Cannot revoke access token; access token is invalid.")

        props = {
            'token' : token,
            'refresh_token' : token
        }

        h = PaymentsApi().send_auth_request(props, 'revoke', PaymentsApi.create_auth_object(auth_args))
        self.__dict__.clear()


################################################################################
# Exceptions
################################################################################


class ApiError(Exception):
    """
       Base class for all API errors.

       @ivar status: HTTP status code (or None if there is no status).
       @ivar reference: reference for the error (or None if there is no reference).
       @ivar error_code: string code for the error (or None if there is no error code).
       @ivar message: string description of the error (or None if there is no message).
       @ivar error_data: dictionary containing all the error data (or None if there is no data)
    """

    def __init__(self, message=None, status=500, error_data=None):
        self.status = status

        self.error_data = json.loads(error_data) if error_data else {}
        err = self.error_data['error'] if 'error' in self.error_data else {}

        self.reference = self.error_data['reference'] if 'reference' in self.error_data else None
        self.error_code = err['code'] if 'code' in err else None
        self.message = err['message'] if 'code' in err else message
        super(ApiError, self).__init__(self.message)


    def describe(self):
        """
           Returns a string describing the error.
           @return: a string describing the error.
        """
        return "{0}: \"{1}\" (status: {2}, error code: {3}, reference: {4})".format(self.__class__.__name__, self.message, self.status, self.error_code, self.reference)


class IllegalArgumentError(ValueError):
    """
       Error raised when passing illegal arguments.
    """
    pass

class ApiConnectionError(ApiError):
    """
       Error raised when there are communication errors contacting the API.
    """
    pass

class AuthenticationError(ApiError):
    """
       Error raised where there are problems authentication a request.
    """
    pass

class BadRequestError(ApiError):

    """
       Error raised when the request contains errors.

       @ivar has_field_errors: boolean indicating whether there are field errors.
       @ivar field_errors: a list containing all field errors.
    """

    class FieldError:
        """
            Represents a single error in a field of data sent in a request to the API.

            @ivar field_name: the name of the field with the error.
            @ivar error_code: a string code for the error.
            @ivar message: a string description of the error.
        """
        def __init__(self, error_data):
            self.field_name = error_data['field']
            self.error_code = error_data['code']
            self.message = error_data['message']
            
        def __str__(self):
            return "Field error: {0} \"{1}\" ({2})".format(self.field_name, self.message, self.error_code)

        
    def __init__(self, message, status = 400, error_data = None):
        super(BadRequestError, self).__init__(message, status, error_data)
        
        self.field_errors = []
        err = self.error_data['error'] if 'error' in self.error_data else {}
        field_errors = err['fieldErrors'] if 'fieldErrors' in err else []
        for field_error in field_errors:
            self.field_errors.append(BadRequestError.FieldError(field_error))
        self.has_field_errors = len(self.field_errors) > 0

    def describe(self):
        """
           Returns a string describing the error.
           @return: a string describing the error.
        """
        txt = ApiError.describe(self)
        for field_error in self.field_errors:
            txt = txt + "\n" + str(field_error)
        return txt + "\n"

class ObjectNotFoundError(ApiError):
    """
       Error raised when a requested object cannot be found.
    """
    pass

class NotAllowedError(ApiError):
    """
       Error raised when a request was not allowed.
    """
    pass

class SysError(ApiError):
    """
       Error raised when there was a system error processing a request.
    """
    pass


################################################################################
# Http - handles the HTTP requests
################################################################################

class Http:
    def __init__(self):
        pass

    def request(self, auth, url, method, params = None):

        if params is None:
            params = {}

        jws_signature = Jws.encode(url, auth, params, method == HTTP_METHOD_POST or method == HTTP_METHOD_PUT)

        if method == HTTP_METHOD_POST:
            request = Request(url, jws_signature)
            request.add_header("Content-Type", "application/json")

        elif method == HTTP_METHOD_PUT:
            request = Request(url, jws_signature)
            request.add_header("Content-Type", "application/json")

        elif method == HTTP_METHOD_DELETE:
            request = Request(url)
            request.add_header("Authorization", "JWS " + jws_signature)
            request.get_method = lambda: HTTP_METHOD_DELETE

        elif method == HTTP_METHOD_GET:
            request = Request(url)
            request.add_header("Authorization", "JWS " + jws_signature)

        else:
            raise ApiConnectionError("HTTP Method {0} not recognised".format(method))

        request.add_header("Accept", "application/json")
        global user_agent

        user_agent_hdr = "Python-SDK/" + Constants.version
        if user_agent != None:
            user_agent_hdr = user_agent_hdr + " " + user_agent
        request.add_header("User-Agent", user_agent_hdr)

        try:
            response = urlopen(request)
            response_body = response.read()
            response_code = response.code
        except HTTPError as err:
            response_body = err.read()
            response_code = err.code
        except URLError as err:
            msg = "Looks like there's a problem connecting to the API endpoint: {0}\nError: {1}".format(url, str(err))
            raise ApiConnectionError(msg)

        return response_body, response_code


    def auth_request(self, auth, url, params):

        jws_signature = Jws.auth_encode(url, auth, params)

        request = Request(url, jws_signature)
        request.add_header("Content-Type", "application/json")
        request.add_header("Accept", "application/json")

        global user_agent
        user_agent_hdr = "Python-SDK/" + Constants.version
        if user_agent != None:
            user_agent_hdr = user_agent_hdr + " " + user_agent
        request.add_header("User-Agent", user_agent_hdr)

        try:
            response = urlopen(request)
            response_body = response.read()
            response_code = response.code
        except HTTPError as err:
            response_body = err.read()
            response_code = err.code
        except URLError as err:
            msg = "Looks like there's a problem connecting to the API endpoint: {0}\nError: {1}".format(url, str(err))
            raise ApiConnectionError(msg)

        return response_body, response_code


################################################################################
# JWS WebHook Utils
################################################################################

class Jws:

    NUM_HEADERS = 7
    ALGORITHM = 'HS256'
    TYPE = 'JWS'
    HDR_URI = 'api.simplifycommerce.com/uri'
    HDR_TIMESTAMP = 'api.simplifycommerce.com/timestamp'
    HDR_NONCE = 'api.simplifycommerce.com/nonce'
    HDR_TOKEN = "api.simplifycommerce.com/token";
    HDR_UNAME = 'uname'
    HDR_ALGORITHM = 'alg'
    HDR_TYPE = 'typ'
    HDR_KEY_ID = 'kid'
    TIMESTAMP_MAX_DIFF = 1000 * 60 * 5   # 5 minutes

    def __init__(self):
        pass

    @staticmethod
    def encode(url, auth, params, has_payload):

        jws_hdr = {'typ': Jws.TYPE,
                   'alg': Jws.ALGORITHM,
                   'kid': auth.public_key,
                   Jws.HDR_URI: url,
                   Jws.HDR_TIMESTAMP: int(round(time.time() * 1000)),
                   Jws.HDR_NONCE: str(random.randint(1, 10*1000))}

        token = auth.access_token
        if token:
            jws_hdr[Jws.HDR_TOKEN] = token

        header = base64.urlsafe_b64encode(Jws().encode_json(jws_hdr)).replace('=', '')
        payload = ''
        if has_payload:
            payload = Jws().encode_json(params)
            payload = base64.urlsafe_b64encode(payload).replace('=', '')

        msg = header + "." + payload
        signature = Jws().sign(auth.private_key, msg)
        return msg + "." + signature


    @staticmethod
    def auth_encode(url, auth, params):

        jws_hdr = {'typ': Jws.TYPE,
                   'alg': Jws.ALGORITHM,
                   'kid': auth.public_key,
                   Jws.HDR_URI: url,
                   Jws.HDR_TIMESTAMP: int(round(time.time() * 1000)),
                   Jws.HDR_NONCE: str(random.randint(1, 10*1000))}

        header = base64.urlsafe_b64encode(Jws().encode_json(jws_hdr)).replace('=', '')

        # Convert map to param string
        payload = '&'.join([ "%s=%s" % (k,v) for k,v in params.iteritems()])
        payload = base64.urlsafe_b64encode(payload).replace('=', '')

        msg = header + "." + payload
        signature = Jws().sign(auth.private_key, msg)
        return msg + "." + signature


    @staticmethod
    def decode(params, auth):

        global public_key
        public_api_key = auth.public_key if auth.public_key else public_key

        if not public_api_key:
            raise IllegalArgumentError("Must have a valid public key to connect to the API")

        global private_key
        private_api_key = auth.private_key if auth.private_key else private_key

        if not private_api_key:
            raise IllegalArgumentError("Must have a valid private key to connect to the API")

        if not 'payload' in params:
            raise IllegalArgumentError("Event data is missing payload")

        payload = params['payload'].strip()
        data = payload.split('.')
        if len(data) != 3:
            raise IllegalArgumentError("Incorrectly formatted JWS message")

        msg = "{0}.{1}".format(data[0], data[1])
        header = Jws().safe_base64_decode(data[0])
        payload = Jws().safe_base64_decode(data[1])
        signature = data[2]

        url = None
        if 'url' in params:
            url = params['url']
        Jws().verify(header, url, public_api_key)

        if signature != Jws().sign(private_api_key, msg):
            raise AuthenticationError("JWS signature does not match")

        return json.loads(payload)

    def sign(self, private_api_key, msg):
        decoded_private_api_key = Jws().safe_base64_decode(private_api_key)
        signature =  hmac.new(decoded_private_api_key, msg, hashlib.sha256).digest()
        return base64.urlsafe_b64encode(signature).replace('=', '')

    def verify(self, header, url, public_api_key):

        hdr = json.loads(header)

        if len(hdr) != Jws.NUM_HEADERS:
            raise AuthenticationError("Incorrect number of JWS header parameters - found {0} but expected {1}".format(len(hdr), Jws.NUM_HEADERS))

        if not Jws.HDR_ALGORITHM in hdr:
            raise AuthenticationError("Missing algorithm header")

        if hdr[Jws.HDR_ALGORITHM] != Jws.ALGORITHM:
            raise AuthenticationError("Incorrect algorithm - found {0} but required {1}".format(hdr[Jws.HDR_ALGORITHM], Jws.ALGORITHM))

        if not Jws.HDR_TYPE in hdr:
            raise AuthenticationError("Missing type header")

        if hdr[Jws.HDR_TYPE] != Jws.TYPE:
            raise AuthenticationError("Incorrect type - found {0} but required {JWS_TYPE}".format(hdr[Jws.HDR_TYPE], Jws.TYPE))

        if not Jws.HDR_KEY_ID in hdr:
            raise AuthenticationError("Missing Key ID")

        # keys don't match and it is a live key
        if hdr[Jws.HDR_KEY_ID] != public_api_key and public_api_key.startswith("lvpb"):
            raise AuthenticationError("Invalid Key ID")

        if not Jws.HDR_NONCE in hdr:
            raise AuthenticationError("Missing nonce")

        if not Jws.HDR_URI in hdr:
            raise AuthenticationError("Missing URI")

        if url != None and hdr[Jws.HDR_URI] != url:
            raise AuthenticationError("Incorrect URL - found {0} but required {1}".format(hdr[Jws.HDR_URI], url))

        if not Jws.HDR_TIMESTAMP in hdr:
            raise AuthenticationError("Missing timestamp")

        if not Jws.HDR_UNAME in hdr:
            raise AuthenticationError("Missing username")

        # calculate time difference between when the request was created and now
        time_now = int(round(time.time() * 1000))
        timestamp = int(hdr[Jws.HDR_TIMESTAMP])
        diff = time_now - timestamp

        if diff > Jws.TIMESTAMP_MAX_DIFF:
            raise AuthenticationError("Invalid timestamp, the event has expired")

    def safe_base64_decode(self, url):

        length = len(url) % 4
        if length == 2:
            return base64.urlsafe_b64decode(url + "==")
        if length == 3:
            return base64.urlsafe_b64decode(url + "=")

        return base64.urlsafe_b64decode(url)

    def encode_json(self, json_str):

        try:
            return json.dumps(json_str).encode('utf-8')
        except Exception:
            raise ApiError("Invalid format for JSON request")


################################################################################
# PaymentsApi
################################################################################

class PaymentsApi:


    def __init__(self):
        pass

    @staticmethod
    def create_auth_object(auth_args):

        global public_key
        global private_key

        if len(auth_args) == 0:
            auth = Authentication(public_key = public_key, private_key = private_key)

        elif len(auth_args) == 1:
            auth = auth_args[0]
            if not isinstance(auth, Authentication):
                raise IllegalArgumentError("Invalid Authentication object passed")

        elif len(auth_args) == 2:
            public_api_key = auth_args[0]
            if public_api_key == None:
                public_api_key = public_key
            private_api_key = auth_args[1]
            if private_api_key == None:
                private_api_key = private_key
            auth = Authentication(public_key = public_api_key, private_key = private_api_key)

        else:
            raise IllegalArgumentError("Invalid authentication arguments passed")

        return auth


    @staticmethod
    def check_auth(auth):

        if auth == None:
            raise IllegalArgumentError("Missing authentication object")

        if auth.public_key == None:
            raise IllegalArgumentError("Must have a valid public key to connect to the API")

        if auth.private_key == None:
            raise IllegalArgumentError("Must have a valid private key to connect to the API")



    @staticmethod
    def create(object_type, auth_args, params):

        auth = PaymentsApi.create_auth_object(auth_args)
        url = PaymentsApi.build_request_url(object_type)
        response = PaymentsApi().execute(object_type, auth, url, HTTP_METHOD_POST, params)

        return response

    @staticmethod
    def list(object_type, auth_args, criteria):

        auth = PaymentsApi.create_auth_object(auth_args)
        url = PaymentsApi.build_request_url(object_type)
        query_string = build_query_string(criteria)
        if len(query_string) > 0:
            url = url + '?' + query_string
        response = PaymentsApi().execute(object_type, auth, url, HTTP_METHOD_GET)

        return response

    @staticmethod
    def find(object_type, auth_args, object_id):

        auth = PaymentsApi.create_auth_object(auth_args)
        if not object_id:
            raise IllegalArgumentError("object_object_id is a required field")

        url = PaymentsApi.build_request_url(object_type, object_id)
        response = PaymentsApi().execute(object_type, auth, url, HTTP_METHOD_GET)

        return response

    @staticmethod
    def update(object_type, auth_args, object_id, params):

        auth = PaymentsApi.create_auth_object(auth_args)
        if not object_id:
            raise IllegalArgumentError("object_id is a required field")

        url = PaymentsApi.build_request_url(object_type, object_id)
        response = PaymentsApi().execute(object_type, auth, url, HTTP_METHOD_PUT, params)

        return response

    @staticmethod
    def delete(object_type, auth_args, object_id):

        auth = PaymentsApi.create_auth_object(auth_args)
        if not object_id:
            raise IllegalArgumentError("object_id is a required field")

        url = PaymentsApi.build_request_url(object_type, object_id)
        response = PaymentsApi().execute(object_type, auth, url, HTTP_METHOD_DELETE)

        return response

    def decode(self, auth_args, params):

        auth = PaymentsApi.create_auth_object(auth_args)
        PaymentsApi.check_auth(auth)

        return Jws.decode(params, auth)


    def execute(self, object_type, auth, url_suffix, method, params = None):

        if params is None:
            params = {}

        PaymentsApi.check_auth(auth)

        http = Http()

        global api_base_sandbox_url
        global api_base_live_url

        base_url = api_base_sandbox_url
        if auth.public_key.startswith('lvpb'):
            base_url = api_base_live_url
        url = base_url + "/" + url_suffix

        response_body, response_code = http.request(auth, url, method, params)

        if not response_code == HTTP_SUCCESS:
            handle_http_error(response_body, response_code)

        try:
            response = json.loads(response_body)
        except Exception:
            raise SysError("Invalid response format returned.  Have you got the correct URL {0} \n HTTP Status: {1}".format(url, response_code))

        if "list" in response:
            obj = DomainFactory.factory("domain")
            obj.list = [DomainFactory.factory(object_type, values) for values in response["list"]]
            obj.total = response["total"]
            return obj
        else:
            return DomainFactory.factory(object_type, response)


    def send_auth_request(self, props, context, auth):

        PaymentsApi.check_auth(auth)

        http = Http()

        global oauth_base_url

        url = oauth_base_url + "/" + context

        response_body, response_code = http.auth_request(auth, url, props)


        try:
            response = json.loads(response_body)
        except Exception:
            raise SysError("Invalid response format returned.  Have you got the correct URL {0} \n HTTP Status: {1}".format(url, response_code))

        if response_code == HTTP_SUCCESS:
            return response
        elif response_code == HTTP_REDIRECTED:
            raise BadRequestError("", response_code)
        elif response_code >= HTTP_BAD_REQUEST:
            error_code = response['error']
            error_desc = response['error_description']
            if error_code == 'invalid_request':
                raise BadRequestError("", response_code, self.get_oauth_error("Error during OAuth request", error_code, error_desc))
            elif error_code == 'access_denied':
                raise AuthenticationError("", response_code, self.get_oauth_error("Access denied for OAuth request", error_code, error_desc))
            elif error_code == 'invalid_client':
                raise AuthenticationError("", response_code, self.get_oauth_error("Invalid client ID in OAuth request", error_code, error_desc))
            elif error_code == 'unauthorized_client':
                raise AuthenticationError("", response_code, self.get_oauth_error("Unauthorized client in OAuth request", error_code, error_desc))
            elif error_code == 'unsupported_grant_type':
                raise BadRequestError("", response_code, self.get_oauth_error("Unsupported grant type in OAuth request", error_code, error_desc))
            elif error_code == 'invalid_scope':
                raise BadRequestError("", response_code, self.get_oauth_error("Invalid scope in OAuth request", error_code, error_desc))
            else:
                raise BadRequestError("", e.response_code, self.get_oauth_error("Unknown OAuth error", error_code, error_desc))
            end
        elif response_code < 500:
            raise BadRequestError("Bad request", response_code, {})
        else:
            raise SysError("Bad request", response_code, {})


    def get_oauth_error(self, msg, error_code, error_desc):
        return  """{"error" : {"code" : "oauth_error", "message" : "%s, error code '%s', description '%s'" }}"""  % (msg, error_code, error_desc)


    @classmethod
    def build_request_url(cls, object_type,  object_id = ''):

        url = object_type
        if object_id:
            url = "{0}/{1}".format(url, object_id)

        return url



################################################################################
# Domain classes
################################################################################


class Event(Domain):

    """
       A Event object.
    """

    @staticmethod
    def create(params, *auth_args):

        """
          Create an Event object.
          @param params: a dict of parameters; valid keys are:
               - C{payload}:  The raw JWS message payload. B{required}
               - C{url}: The URL for the webhook.  If present it must match the URL registered for the webhook.
          @param auth_args: an Authentication object used for the API call.  If no value is passed the gloabl keys simplify.public_key and simplify.private_key are used.
              For backwards compatibility the public and private keys may be passed instead of an Authentication object.
          @return: an Event object
        """

        obj = PaymentsApi().decode(auth_args, params)

        if not 'event' in obj:
            raise ApiError("Incorrect data in webhook event")

        return DomainFactory.factory('event', obj['event'])

class CardToken(Domain):
    """
       A CardToken object.
    """


    @staticmethod
    def create(params, *auth_args):
        """
          Creates an CardToken object
          @param params: a dict of parameters; valid keys are:
              - C{callback}:  The URL callback for the cardtoken 
              - C{card => addressCity}:  City of the cardholder. 
              - C{card => addressCountry}:  Country code (ISO-3166-1-alpha-2 code) of residence of the cardholder. 
              - C{card => addressLine1}:  Address of the cardholder. 
              - C{card => addressLine2}:  Address of the cardholder if needed. 
              - C{card => addressState}:  State code (USPS code) of residence of the cardholder. 
              - C{card => addressZip}:  Postal code of the cardholder. 
              - C{card => cvc}:  CVC security code of the card. This is the code on the back of the card. Example: 123 
              - C{card => expMonth}:  Expiration month of the card. Format is MM. Example: January = 01 B{required }
              - C{card => expYear}:  Expiration year of the card. Format is YY. Example: 2013 = 13 B{required }
              - C{card => name}:  Name as appears on the card. 
              - C{card => number}:  Card number as it appears on the card. B{required }
              - C{key}:  Key used to create the card token. 
          @param auth_args: an Authentication object used for the API call.  If no value is passed the gloabl keys simplify.public_key and simplify.private_key are used.
              For backwards compatibility the public and private keys may be passed instead of an Authentication object.
          @param private_api_key: Private key to use for the API call. If C{None}, the value of C{simplify.private_key} will be used.
          @return: a CardToken object
        """
        return PaymentsApi.create("cardToken", auth_args, params)

    @staticmethod
    def find(object_id, *auth_args):
        """
          Retrieve a CardToken object from the API
          @param object_id: ID of object to retrieve
          @param auth_args: an Authentication object used for the API call.  If no value is passed the gloabl keys simplify.public_key and simplify.private_key are used.
              For backwards compatibility the public and private keys may be passed instead of an Authentication object.
          @return: a CardToken object
        """
        return PaymentsApi.find("cardToken", auth_args, object_id)

class Chargeback(Domain):
    """
       A Chargeback object.
    """


    @staticmethod
    def list(criteria = None, *auth_args):
        """
          Retrieve Chargeback objects.
          @param criteria: a dict of parameters; valid keys are:
               - C{filter}  Filters to apply to the list. 
               - C{max}  Allows up to a max of 50 list items to return. B{default:20}
               - C{offset}  Used in paging of the list.  This is the start offset of the page. B{default:0}
               - C{sorting}  Allows for ascending or descending sorting of the list. The value maps properties to the sort direction (either C{asc} for ascending or C{desc} for descending).  Sortable properties are:  C{id} C{amount} C{description} C{dateCreated}.
          @param auth_args: an Authentication object used for the API call.  If no value is passed the gloabl keys simplify.public_key and simplify.private_key are used.
              For backwards compatibility the public and private keys may be passed instead of an Authentication object.
          @return: an object which contains the list of Chargeback objects in the <code>list</code> property and the total number
                   of objects available for the given criteria in the <code>total</code> property.
        """
        return PaymentsApi.list("chargeback", auth_args, criteria)

    @staticmethod
    def find(object_id, *auth_args):
        """
          Retrieve a Chargeback object from the API
          @param object_id: ID of object to retrieve
          @param auth_args: an Authentication object used for the API call.  If no value is passed the gloabl keys simplify.public_key and simplify.private_key are used.
              For backwards compatibility the public and private keys may be passed instead of an Authentication object.
          @return: a Chargeback object
        """
        return PaymentsApi.find("chargeback", auth_args, object_id)

class Coupon(Domain):
    """
       A Coupon object.
    """


    @staticmethod
    def create(params, *auth_args):
        """
          Creates an Coupon object
          @param params: a dict of parameters; valid keys are:
              - C{amountOff}:  Amount off of the price of the product in minor units in the currency of the merchant. While this field is optional, you must provide either amountOff or percentOff for a coupon. Example: 1000 = 10.00 
              - C{couponCode}:  Code that identifies the coupon to be used. B{required }
              - C{description}:  A brief section that describes the coupon. 
              - C{durationInMonths}:  Duration in months that the coupon will be applied after it has first been selected. 
              - C{endDate}:  Last date of the coupon in UTC millis that the coupon can be applied to a subscription. This ends at 23:59:59 of the merchant timezone. 
              - C{maxRedemptions}:  Maximum number of redemptions allowed for the coupon. A redemption is defined as when the coupon is applied to the subscription for the first time. 
              - C{percentOff}:  Percentage off of the price of the product. While this field is optional, you must provide either amountOff or percentOff for a coupon. The percent off is a whole number. 
              - C{startDate}:  First date of the coupon in UTC millis that the coupon can be applied to a subscription. This starts at midnight of the merchant timezone. B{required }
          @param auth_args: an Authentication object used for the API call.  If no value is passed the gloabl keys simplify.public_key and simplify.private_key are used.
              For backwards compatibility the public and private keys may be passed instead of an Authentication object.
          @param private_api_key: Private key to use for the API call. If C{None}, the value of C{simplify.private_key} will be used.
          @return: a Coupon object
        """
        return PaymentsApi.create("coupon", auth_args, params)

    def delete(self, *auth_args):
        """
            Delete this object
            @param auth_args: an Authentication object used for the API call.  If no value is passed the gloabl keys simplify.public_key and simplify.private_key are used.
                For backwards compatibility the public and private keys may be passed instead of an Authentication object.
        """
        return PaymentsApi.delete("coupon", auth_args, self.object_id)

    @staticmethod
    def list(criteria = None, *auth_args):
        """
          Retrieve Coupon objects.
          @param criteria: a dict of parameters; valid keys are:
               - C{filter}  Filters to apply to the list. 
               - C{max}  Allows up to a max of 50 list items to return. B{default:20}
               - C{offset}  Used in paging of the list.  This is the start offset of the page. B{default:0}
               - C{sorting}  Allows for ascending or descending sorting of the list. The value maps properties to the sort direction (either C{asc} for ascending or C{desc} for descending).  Sortable properties are:  C{dateCreated} C{maxRedemptions} C{timesRedeemed} C{id} C{startDate} C{endDate} C{percentOff} C{couponCode} C{durationInMonths} C{amountOff}.
          @param auth_args: an Authentication object used for the API call.  If no value is passed the gloabl keys simplify.public_key and simplify.private_key are used.
              For backwards compatibility the public and private keys may be passed instead of an Authentication object.
          @return: an object which contains the list of Coupon objects in the <code>list</code> property and the total number
                   of objects available for the given criteria in the <code>total</code> property.
        """
        return PaymentsApi.list("coupon", auth_args, criteria)

    @staticmethod
    def find(object_id, *auth_args):
        """
          Retrieve a Coupon object from the API
          @param object_id: ID of object to retrieve
          @param auth_args: an Authentication object used for the API call.  If no value is passed the gloabl keys simplify.public_key and simplify.private_key are used.
              For backwards compatibility the public and private keys may be passed instead of an Authentication object.
          @return: a Coupon object
        """
        return PaymentsApi.find("coupon", auth_args, object_id)

    def update(self, *auth_args):
        """
          Updates this object

          The properties that can be updated:  
            - C{endDate} The ending date in UTC millis for the coupon. This must be after the starting date of the coupon. 

            - C{maxRedemptions} Maximum number of redemptions allowed for the coupon. A redemption is defined as when the coupon is applied to the subscription for the first time. 

          @param auth_args: an Authentication object used for the API call.  If no value is passed the gloabl keys simplify.public_key and simplify.private_key are used.
              For backwards compatibility the public and private keys may be passed instead of an Authentication object.
          @return: a Coupon object.
        """
        return PaymentsApi.update("coupon", auth_args, self.object_id, self.to_dict())

class Customer(Domain):
    """
       A Customer object.
    """


    @staticmethod
    def create(params, *auth_args):
        """
          Creates an Customer object
          @param params: a dict of parameters; valid keys are:
              - C{card => addressCity}:  City of the cardholder. 
              - C{card => addressCountry}:  Country code (ISO-3166-1-alpha-2 code) of residence of the cardholder. 
              - C{card => addressLine1}:  Address of the cardholder 
              - C{card => addressLine2}:  Address of the cardholder if needed. 
              - C{card => addressState}:  State code (USPS code) of residence of the cardholder. 
              - C{card => addressZip}:  Postal code of the cardholder. 
              - C{card => cvc}:  CVC security code of the card. This is the code on the back of the card. Example: 123 
              - C{card => expMonth}:  Expiration month of the card. Format is MM. Example: January = 01 B{required }
              - C{card => expYear}:  Expiration year of the card. Format is YY. Example: 2013 = 13 B{required }
              - C{card => name}:  Name as appears on the card. 
              - C{card => number}:  Card number as it appears on the card. B{required }
              - C{email}:  Email address of the customer B{required }
              - C{name}:  Customer name B{required }
              - C{reference}:  Reference field for external applications use. 
              - C{subscriptions => amount}:  Amount of payment in minor units. Example: 1000 = 10.00 
              - C{subscriptions => coupon}:  Coupon associated with the subscription for the customer. 
              - C{subscriptions => currency}:  Currency code (ISO-4217). Must match the currency associated with your account. B{default:USD}
              - C{subscriptions => customer}:  The customer ID to create the subscription for. Do not supply this when creating a customer. 
              - C{subscriptions => frequency}:  Frequency of payment for the plan. Example: Monthly 
              - C{subscriptions => name}:  Name describing subscription 
              - C{subscriptions => plan}:  The plan ID that the subscription should be created from. 
              - C{subscriptions => quantity}:  Quantity of the plan for the subscription. 
              - C{token}:  If specified, card associated with card token will be used 
          @param auth_args: an Authentication object used for the API call.  If no value is passed the gloabl keys simplify.public_key and simplify.private_key are used.
              For backwards compatibility the public and private keys may be passed instead of an Authentication object.
          @param private_api_key: Private key to use for the API call. If C{None}, the value of C{simplify.private_key} will be used.
          @return: a Customer object
        """
        return PaymentsApi.create("customer", auth_args, params)

    def delete(self, *auth_args):
        """
            Delete this object
            @param auth_args: an Authentication object used for the API call.  If no value is passed the gloabl keys simplify.public_key and simplify.private_key are used.
                For backwards compatibility the public and private keys may be passed instead of an Authentication object.
        """
        return PaymentsApi.delete("customer", auth_args, self.object_id)

    @staticmethod
    def list(criteria = None, *auth_args):
        """
          Retrieve Customer objects.
          @param criteria: a dict of parameters; valid keys are:
               - C{filter}  Filters to apply to the list. 
               - C{max}  Allows up to a max of 50 list items to return. B{default:20}
               - C{offset}  Used in paging of the list.  This is the start offset of the page. B{default:0}
               - C{sorting}  Allows for ascending or descending sorting of the list. The value maps properties to the sort direction (either C{asc} for ascending or C{desc} for descending).  Sortable properties are:  C{dateCreated} C{id} C{name} C{email} C{reference}.
          @param auth_args: an Authentication object used for the API call.  If no value is passed the gloabl keys simplify.public_key and simplify.private_key are used.
              For backwards compatibility the public and private keys may be passed instead of an Authentication object.
          @return: an object which contains the list of Customer objects in the <code>list</code> property and the total number
                   of objects available for the given criteria in the <code>total</code> property.
        """
        return PaymentsApi.list("customer", auth_args, criteria)

    @staticmethod
    def find(object_id, *auth_args):
        """
          Retrieve a Customer object from the API
          @param object_id: ID of object to retrieve
          @param auth_args: an Authentication object used for the API call.  If no value is passed the gloabl keys simplify.public_key and simplify.private_key are used.
              For backwards compatibility the public and private keys may be passed instead of an Authentication object.
          @return: a Customer object
        """
        return PaymentsApi.find("customer", auth_args, object_id)

    def update(self, *auth_args):
        """
          Updates this object

          The properties that can be updated:  
            - C{card => addressCity} City of the cardholder. 

            - C{card => addressCountry} Country code (ISO-3166-1-alpha-2 code) of residence of the cardholder. 

            - C{card => addressLine1} Address of the cardholder. 

            - C{card => addressLine2} Address of the cardholder if needed. 

            - C{card => addressState} State code (USPS code) of residence of the cardholder. 

            - C{card => addressZip} Postal code of the cardholder. 

            - C{card => cvc} CVC security code of the card. This is the code on the back of the card. Example: 123 

            - C{card => expMonth} Expiration month of the card. Format is MM.  Example: January = 01 B{(required)}

            - C{card => expYear} Expiration year of the card. Format is YY. Example: 2013 = 13 B{(required)}

            - C{card => name} Name as appears on the card. 

            - C{card => number} Card number as it appears on the card. B{(required)}

            - C{email} Email address of the customer B{(required)}

            - C{name} Customer name B{(required)}

            - C{reference} Reference field for external applications use. 

          @param auth_args: an Authentication object used for the API call.  If no value is passed the gloabl keys simplify.public_key and simplify.private_key are used.
              For backwards compatibility the public and private keys may be passed instead of an Authentication object.
          @return: a Customer object.
        """
        return PaymentsApi.update("customer", auth_args, self.object_id, self.to_dict())

class Deposit(Domain):
    """
       A Deposit object.
    """


    @staticmethod
    def list(criteria = None, *auth_args):
        """
          Retrieve Deposit objects.
          @param criteria: a dict of parameters; valid keys are:
               - C{filter}  Filters to apply to the list. 
               - C{max}  Allows up to a max of 50 list items to return. B{default:20}
               - C{offset}  Used in paging of the list.  This is the start offset of the page. B{default:0}
               - C{sorting}  Allows for ascending or descending sorting of the list. The value maps properties to the sort direction (either C{asc} for ascending or C{desc} for descending).  Sortable properties are:  C{amount} C{dateCreated} C{depositDate}.
          @param auth_args: an Authentication object used for the API call.  If no value is passed the gloabl keys simplify.public_key and simplify.private_key are used.
              For backwards compatibility the public and private keys may be passed instead of an Authentication object.
          @return: an object which contains the list of Deposit objects in the <code>list</code> property and the total number
                   of objects available for the given criteria in the <code>total</code> property.
        """
        return PaymentsApi.list("deposit", auth_args, criteria)

    @staticmethod
    def find(object_id, *auth_args):
        """
          Retrieve a Deposit object from the API
          @param object_id: ID of object to retrieve
          @param auth_args: an Authentication object used for the API call.  If no value is passed the gloabl keys simplify.public_key and simplify.private_key are used.
              For backwards compatibility the public and private keys may be passed instead of an Authentication object.
          @return: a Deposit object
        """
        return PaymentsApi.find("deposit", auth_args, object_id)

class Invoice(Domain):
    """
       A Invoice object.
    """


    @staticmethod
    def list(criteria = None, *auth_args):
        """
          Retrieve Invoice objects.
          @param criteria: a dict of parameters; valid keys are:
               - C{filter}  Filters to apply to the list. 
               - C{max}  Allows up to a max of 50 list items to return. B{default:20}
               - C{offset}  Used in paging of the list.  This is the start offset of the page. B{default:0}
               - C{sorting}  Allows for ascending or descending sorting of the list. The value maps properties to the sort direction (either C{asc} for ascending or C{desc} for descending).  Sortable properties are:  C{id} C{invoiceDate} C{customer} C{amount} C{processedDate}.
          @param auth_args: an Authentication object used for the API call.  If no value is passed the gloabl keys simplify.public_key and simplify.private_key are used.
              For backwards compatibility the public and private keys may be passed instead of an Authentication object.
          @return: an object which contains the list of Invoice objects in the <code>list</code> property and the total number
                   of objects available for the given criteria in the <code>total</code> property.
        """
        return PaymentsApi.list("invoice", auth_args, criteria)

    @staticmethod
    def find(object_id, *auth_args):
        """
          Retrieve a Invoice object from the API
          @param object_id: ID of object to retrieve
          @param auth_args: an Authentication object used for the API call.  If no value is passed the gloabl keys simplify.public_key and simplify.private_key are used.
              For backwards compatibility the public and private keys may be passed instead of an Authentication object.
          @return: a Invoice object
        """
        return PaymentsApi.find("invoice", auth_args, object_id)

    def update(self, *auth_args):
        """
          Updates this object

          The properties that can be updated:  
            - C{status} Status of the invoice. Examples: OPEN = Invoice has not been processed and can have invoice items added to it. PAID = Invoice has been paid. UNPAID = Invoice was not paid when the card was processed. System will try up to 5 times to process the card. B{(required)}

          @param auth_args: an Authentication object used for the API call.  If no value is passed the gloabl keys simplify.public_key and simplify.private_key are used.
              For backwards compatibility the public and private keys may be passed instead of an Authentication object.
          @return: a Invoice object.
        """
        return PaymentsApi.update("invoice", auth_args, self.object_id, self.to_dict())

class InvoiceItem(Domain):
    """
       A InvoiceItem object.
    """


    @staticmethod
    def create(params, *auth_args):
        """
          Creates an InvoiceItem object
          @param params: a dict of parameters; valid keys are:
              - C{amount}:  Amount of the invoice item (minor units). Example: 1000 = 10.00 B{required }
              - C{currency}:  Currency code (ISO-4217) for the invoice item. Must match the currency associated with your account. B{required }B{default:USD}
              - C{description}:  Individual items of an invoice 
              - C{invoice}:  Description of the invoice item B{required }
          @param auth_args: an Authentication object used for the API call.  If no value is passed the gloabl keys simplify.public_key and simplify.private_key are used.
              For backwards compatibility the public and private keys may be passed instead of an Authentication object.
          @param private_api_key: Private key to use for the API call. If C{None}, the value of C{simplify.private_key} will be used.
          @return: a InvoiceItem object
        """
        return PaymentsApi.create("invoiceItem", auth_args, params)

    def delete(self, *auth_args):
        """
            Delete this object
            @param auth_args: an Authentication object used for the API call.  If no value is passed the gloabl keys simplify.public_key and simplify.private_key are used.
                For backwards compatibility the public and private keys may be passed instead of an Authentication object.
        """
        return PaymentsApi.delete("invoiceItem", auth_args, self.object_id)

    @staticmethod
    def list(criteria = None, *auth_args):
        """
          Retrieve InvoiceItem objects.
          @param criteria: a dict of parameters; valid keys are:
               - C{filter}  Filters to apply to the list. 
               - C{max}  Allows up to a max of 50 list items to return. B{default:20}
               - C{offset}  Used in paging of the list.  This is the start offset of the page. B{default:0}
               - C{sorting}  Allows for ascending or descending sorting of the list. The value maps properties to the sort direction (either C{asc} for ascending or C{desc} for descending).  Sortable properties are:  C{id} C{amount} C{description} C{invoice}.
          @param auth_args: an Authentication object used for the API call.  If no value is passed the gloabl keys simplify.public_key and simplify.private_key are used.
              For backwards compatibility the public and private keys may be passed instead of an Authentication object.
          @return: an object which contains the list of InvoiceItem objects in the <code>list</code> property and the total number
                   of objects available for the given criteria in the <code>total</code> property.
        """
        return PaymentsApi.list("invoiceItem", auth_args, criteria)

    @staticmethod
    def find(object_id, *auth_args):
        """
          Retrieve a InvoiceItem object from the API
          @param object_id: ID of object to retrieve
          @param auth_args: an Authentication object used for the API call.  If no value is passed the gloabl keys simplify.public_key and simplify.private_key are used.
              For backwards compatibility the public and private keys may be passed instead of an Authentication object.
          @return: a InvoiceItem object
        """
        return PaymentsApi.find("invoiceItem", auth_args, object_id)

    def update(self, *auth_args):
        """
          Updates this object

          The properties that can be updated:  
            - C{amount} Amount of the invoice item (minor units). Example: 1000 = 10.00 

            - C{currency} Currency code (ISO-4217) for the invoice item. Must match the currency associated with your account. 

            - C{description} Individual items of an invoice 

          @param auth_args: an Authentication object used for the API call.  If no value is passed the gloabl keys simplify.public_key and simplify.private_key are used.
              For backwards compatibility the public and private keys may be passed instead of an Authentication object.
          @return: a InvoiceItem object.
        """
        return PaymentsApi.update("invoiceItem", auth_args, self.object_id, self.to_dict())

class Payment(Domain):
    """
       A Payment object.
    """


    @staticmethod
    def create(params, *auth_args):
        """
          Creates an Payment object
          @param params: a dict of parameters; valid keys are:
              - C{amount}:  Amount of the payment (minor units). Example: 1000 = 10.00 B{required }
              - C{card => addressCity}:  City of the cardholder. 
              - C{card => addressCountry}:  Country code (ISO-3166-1-alpha-2 code) of residence of the cardholder. 
              - C{card => addressLine1}:  Address of the cardholder. 
              - C{card => addressLine2}:  Address of the cardholder if needed. 
              - C{card => addressState}:  State code (USPS code) of residence of the cardholder. 
              - C{card => addressZip}:  Postal code of the cardholder. 
              - C{card => cvc}:  CVC security code of the card. This is the code on the back of the card. Example: 123 
              - C{card => expMonth}:  Expiration month of the card. Format is MM. Example: January = 01 B{required }
              - C{card => expYear}:  Expiration year of the card. Format is YY. Example: 2013 = 13 B{required }
              - C{card => name}:  Name as it appears on the card. 
              - C{card => number}:  Card number as it appears on the card. B{required }
              - C{currency}:  Currency code (ISO-4217) for the transaction. Must match the currency associated with your account. B{required }B{default:USD}
              - C{customer}:  ID of customer. If specified, card on file of customer will be used. 
              - C{description}:  Custom naming of payment for external systems to use. 
              - C{reference}:  Custom reference field to be used with outside systems. 
              - C{token}:  If specified, card associated with card token will be used. 
          @param auth_args: an Authentication object used for the API call.  If no value is passed the gloabl keys simplify.public_key and simplify.private_key are used.
              For backwards compatibility the public and private keys may be passed instead of an Authentication object.
          @param private_api_key: Private key to use for the API call. If C{None}, the value of C{simplify.private_key} will be used.
          @return: a Payment object
        """
        return PaymentsApi.create("payment", auth_args, params)

    @staticmethod
    def list(criteria = None, *auth_args):
        """
          Retrieve Payment objects.
          @param criteria: a dict of parameters; valid keys are:
               - C{filter}  Filters to apply to the list. 
               - C{max}  Allows up to a max of 50 list items to return. B{default:20}
               - C{offset}  Used in paging of the list.  This is the start offset of the page. B{default:0}
               - C{sorting}  Allows for ascending or descending sorting of the list. The value maps properties to the sort direction (either C{asc} for ascending or C{desc} for descending).  Sortable properties are:  C{dateCreated} C{amount} C{id} C{description} C{paymentDate}.
          @param auth_args: an Authentication object used for the API call.  If no value is passed the gloabl keys simplify.public_key and simplify.private_key are used.
              For backwards compatibility the public and private keys may be passed instead of an Authentication object.
          @return: an object which contains the list of Payment objects in the <code>list</code> property and the total number
                   of objects available for the given criteria in the <code>total</code> property.
        """
        return PaymentsApi.list("payment", auth_args, criteria)

    @staticmethod
    def find(object_id, *auth_args):
        """
          Retrieve a Payment object from the API
          @param object_id: ID of object to retrieve
          @param auth_args: an Authentication object used for the API call.  If no value is passed the gloabl keys simplify.public_key and simplify.private_key are used.
              For backwards compatibility the public and private keys may be passed instead of an Authentication object.
          @return: a Payment object
        """
        return PaymentsApi.find("payment", auth_args, object_id)

class Plan(Domain):
    """
       A Plan object.
    """


    @staticmethod
    def create(params, *auth_args):
        """
          Creates an Plan object
          @param params: a dict of parameters; valid keys are:
              - C{amount}:  Amount of payment for the plan in minor units. Example: 1000 = 10.00 B{required }
              - C{currency}:  Currency code (ISO-4217) for the plan. Must match the currency associated with your account. B{required }B{default:USD}
              - C{frequency}:  Frequency of payment for the plan. Example: Monthly B{required }
              - C{name}:  Name of the plan B{required }
          @param auth_args: an Authentication object used for the API call.  If no value is passed the gloabl keys simplify.public_key and simplify.private_key are used.
              For backwards compatibility the public and private keys may be passed instead of an Authentication object.
          @param private_api_key: Private key to use for the API call. If C{None}, the value of C{simplify.private_key} will be used.
          @return: a Plan object
        """
        return PaymentsApi.create("plan", auth_args, params)

    def delete(self, *auth_args):
        """
            Delete this object
            @param auth_args: an Authentication object used for the API call.  If no value is passed the gloabl keys simplify.public_key and simplify.private_key are used.
                For backwards compatibility the public and private keys may be passed instead of an Authentication object.
        """
        return PaymentsApi.delete("plan", auth_args, self.object_id)

    @staticmethod
    def list(criteria = None, *auth_args):
        """
          Retrieve Plan objects.
          @param criteria: a dict of parameters; valid keys are:
               - C{filter}  Filters to apply to the list. 
               - C{max}  Allows up to a max of 50 list items to return. B{default:20}
               - C{offset}  Used in paging of the list.  This is the start offset of the page. B{default:0}
               - C{sorting}  Allows for ascending or descending sorting of the list. The value maps properties to the sort direction (either C{asc} for ascending or C{desc} for descending).  Sortable properties are:  C{dateCreated} C{amount} C{frequency} C{name} C{id}.
          @param auth_args: an Authentication object used for the API call.  If no value is passed the gloabl keys simplify.public_key and simplify.private_key are used.
              For backwards compatibility the public and private keys may be passed instead of an Authentication object.
          @return: an object which contains the list of Plan objects in the <code>list</code> property and the total number
                   of objects available for the given criteria in the <code>total</code> property.
        """
        return PaymentsApi.list("plan", auth_args, criteria)

    @staticmethod
    def find(object_id, *auth_args):
        """
          Retrieve a Plan object from the API
          @param object_id: ID of object to retrieve
          @param auth_args: an Authentication object used for the API call.  If no value is passed the gloabl keys simplify.public_key and simplify.private_key are used.
              For backwards compatibility the public and private keys may be passed instead of an Authentication object.
          @return: a Plan object
        """
        return PaymentsApi.find("plan", auth_args, object_id)

    def update(self, *auth_args):
        """
          Updates this object

          The properties that can be updated:  
            - C{name} Name of the plan. B{(required)}

          @param auth_args: an Authentication object used for the API call.  If no value is passed the gloabl keys simplify.public_key and simplify.private_key are used.
              For backwards compatibility the public and private keys may be passed instead of an Authentication object.
          @return: a Plan object.
        """
        return PaymentsApi.update("plan", auth_args, self.object_id, self.to_dict())

class Refund(Domain):
    """
       A Refund object.
    """


    @staticmethod
    def create(params, *auth_args):
        """
          Creates an Refund object
          @param params: a dict of parameters; valid keys are:
              - C{amount}:  Amount of the refund in minor units. Example: 1000 = 10.00 B{required }
              - C{payment}:  ID of the payment for the refund B{required }
              - C{reason}:  Reason for the refund 
              - C{reference}:  Custom reference field to be used with outside systems. 
          @param auth_args: an Authentication object used for the API call.  If no value is passed the gloabl keys simplify.public_key and simplify.private_key are used.
              For backwards compatibility the public and private keys may be passed instead of an Authentication object.
          @param private_api_key: Private key to use for the API call. If C{None}, the value of C{simplify.private_key} will be used.
          @return: a Refund object
        """
        return PaymentsApi.create("refund", auth_args, params)

    @staticmethod
    def list(criteria = None, *auth_args):
        """
          Retrieve Refund objects.
          @param criteria: a dict of parameters; valid keys are:
               - C{filter}  Filters to apply to the list. 
               - C{max}  Allows up to a max of 50 list items to return. B{default:20}
               - C{offset}  Used in paging of the list.  This is the start offset of the page. B{default:0}
               - C{sorting}  Allows for ascending or descending sorting of the list. The value maps properties to the sort direction (either C{asc} for ascending or C{desc} for descending).  Sortable properties are:  C{id} C{amount} C{description} C{dateCreated} C{paymentDate}.
          @param auth_args: an Authentication object used for the API call.  If no value is passed the gloabl keys simplify.public_key and simplify.private_key are used.
              For backwards compatibility the public and private keys may be passed instead of an Authentication object.
          @return: an object which contains the list of Refund objects in the <code>list</code> property and the total number
                   of objects available for the given criteria in the <code>total</code> property.
        """
        return PaymentsApi.list("refund", auth_args, criteria)

    @staticmethod
    def find(object_id, *auth_args):
        """
          Retrieve a Refund object from the API
          @param object_id: ID of object to retrieve
          @param auth_args: an Authentication object used for the API call.  If no value is passed the gloabl keys simplify.public_key and simplify.private_key are used.
              For backwards compatibility the public and private keys may be passed instead of an Authentication object.
          @return: a Refund object
        """
        return PaymentsApi.find("refund", auth_args, object_id)

class Subscription(Domain):
    """
       A Subscription object.
    """


    @staticmethod
    def create(params, *auth_args):
        """
          Creates an Subscription object
          @param params: a dict of parameters; valid keys are:
              - C{amount}:  Amount of the payment (minor units). Example: 1000 = 10.00 
              - C{coupon}:  Coupon ID associated with the subscription 
              - C{currency}:  Currency code (ISO-4217). Must match the currency associated with your account. B{default:USD}
              - C{customer}:  Customer that is enrolling in the subscription. 
              - C{frequency}:  Frequency of payment for the plan. Example: Monthly 
              - C{name}:  Name describing subscription 
              - C{plan}:  The ID of the plan that should be used for the subscription. 
              - C{quantity}:  Quantity of the plan for the subscription. 
          @param auth_args: an Authentication object used for the API call.  If no value is passed the gloabl keys simplify.public_key and simplify.private_key are used.
              For backwards compatibility the public and private keys may be passed instead of an Authentication object.
          @param private_api_key: Private key to use for the API call. If C{None}, the value of C{simplify.private_key} will be used.
          @return: a Subscription object
        """
        return PaymentsApi.create("subscription", auth_args, params)

    def delete(self, *auth_args):
        """
            Delete this object
            @param auth_args: an Authentication object used for the API call.  If no value is passed the gloabl keys simplify.public_key and simplify.private_key are used.
                For backwards compatibility the public and private keys may be passed instead of an Authentication object.
        """
        return PaymentsApi.delete("subscription", auth_args, self.object_id)

    @staticmethod
    def list(criteria = None, *auth_args):
        """
          Retrieve Subscription objects.
          @param criteria: a dict of parameters; valid keys are:
               - C{filter}  Filters to apply to the list. 
               - C{max}  Allows up to a max of 50 list items to return. B{default:20}
               - C{offset}  Used in paging of the list.  This is the start offset of the page. B{default:0}
               - C{sorting}  Allows for ascending or descending sorting of the list. The value maps properties to the sort direction (either C{asc} for ascending or C{desc} for descending).  Sortable properties are:  C{id} C{plan}.
          @param auth_args: an Authentication object used for the API call.  If no value is passed the gloabl keys simplify.public_key and simplify.private_key are used.
              For backwards compatibility the public and private keys may be passed instead of an Authentication object.
          @return: an object which contains the list of Subscription objects in the <code>list</code> property and the total number
                   of objects available for the given criteria in the <code>total</code> property.
        """
        return PaymentsApi.list("subscription", auth_args, criteria)

    @staticmethod
    def find(object_id, *auth_args):
        """
          Retrieve a Subscription object from the API
          @param object_id: ID of object to retrieve
          @param auth_args: an Authentication object used for the API call.  If no value is passed the gloabl keys simplify.public_key and simplify.private_key are used.
              For backwards compatibility the public and private keys may be passed instead of an Authentication object.
          @return: a Subscription object
        """
        return PaymentsApi.find("subscription", auth_args, object_id)

    def update(self, *auth_args):
        """
          Updates this object

          The properties that can be updated:  
            - C{amount} Amount of the payment (minor units). Example: 1000 = 10.00 

            - C{coupon} Coupon being assigned to this subscription 

            - C{currency} Currency code (ISO-4217). Must match the currency associated with your account. 

            - C{frequency} Frequency of payment for the plan. Example: Monthly 

            - C{name} Name describing subscription 

            - C{plan} Plan that should be used for the subscription. 

            - C{prorate} Whether to prorate existing subscription. B{(required)}

            - C{quantity} Quantity of the plan for the subscription. 

          @param auth_args: an Authentication object used for the API call.  If no value is passed the gloabl keys simplify.public_key and simplify.private_key are used.
              For backwards compatibility the public and private keys may be passed instead of an Authentication object.
          @return: a Subscription object.
        """
        return PaymentsApi.update("subscription", auth_args, self.object_id, self.to_dict())

class Webhook(Domain):
    """
       A Webhook object.
    """


    @staticmethod
    def create(params, *auth_args):
        """
          Creates an Webhook object
          @param params: a dict of parameters; valid keys are:
              - C{url}:  Endpoint URL B{required }
          @param auth_args: an Authentication object used for the API call.  If no value is passed the gloabl keys simplify.public_key and simplify.private_key are used.
              For backwards compatibility the public and private keys may be passed instead of an Authentication object.
          @param private_api_key: Private key to use for the API call. If C{None}, the value of C{simplify.private_key} will be used.
          @return: a Webhook object
        """
        return PaymentsApi.create("webhook", auth_args, params)

    def delete(self, *auth_args):
        """
            Delete this object
            @param auth_args: an Authentication object used for the API call.  If no value is passed the gloabl keys simplify.public_key and simplify.private_key are used.
                For backwards compatibility the public and private keys may be passed instead of an Authentication object.
        """
        return PaymentsApi.delete("webhook", auth_args, self.object_id)

    @staticmethod
    def list(criteria = None, *auth_args):
        """
          Retrieve Webhook objects.
          @param criteria: a dict of parameters; valid keys are:
               - C{filter}  Filters to apply to the list. 
               - C{max}  Allows up to a max of 50 list items to return. B{default:20}
               - C{offset}  Used in paging of the list.  This is the start offset of the page. B{default:0}
               - C{sorting}  Allows for ascending or descending sorting of the list. The value maps properties to the sort direction (either C{asc} for ascending or C{desc} for descending).  Sortable properties are:  C{dateCreated}.
          @param auth_args: an Authentication object used for the API call.  If no value is passed the gloabl keys simplify.public_key and simplify.private_key are used.
              For backwards compatibility the public and private keys may be passed instead of an Authentication object.
          @return: an object which contains the list of Webhook objects in the <code>list</code> property and the total number
                   of objects available for the given criteria in the <code>total</code> property.
        """
        return PaymentsApi.list("webhook", auth_args, criteria)

    @staticmethod
    def find(object_id, *auth_args):
        """
          Retrieve a Webhook object from the API
          @param object_id: ID of object to retrieve
          @param auth_args: an Authentication object used for the API call.  If no value is passed the gloabl keys simplify.public_key and simplify.private_key are used.
              For backwards compatibility the public and private keys may be passed instead of an Authentication object.
          @return: a Webhook object
        """
        return PaymentsApi.find("webhook", auth_args, object_id)

    def update(self, *auth_args):
        """
          Updates this object

          The properties that can be updated:  
            - C{url} Endpoint URL B{(required)}

          @param auth_args: an Authentication object used for the API call.  If no value is passed the gloabl keys simplify.public_key and simplify.private_key are used.
              For backwards compatibility the public and private keys may be passed instead of an Authentication object.
          @return: a Webhook object.
        """
        return PaymentsApi.update("webhook", auth_args, self.object_id, self.to_dict())
