#!/usr/bin/env python3.2
#
# Copyright (c) Net24 Limited, Christchurch, New Zealand 2011-2012
#       and     Voyager Internet Ltd, New Zealand, 2012-2013
#
#    This file is part of py-magcode-core.
#
#    Py-magcode-core is free software: you can redistribute it and/or modify
#    it under the terms of the GNU  General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Py-magcode-core is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU  General Public License for more details.
#
#    You should have received a copy of the GNU  General Public License
#    along with py-magcode-core.  If not, see <http://www.gnu.org/licenses/>.
#
"""
WSGI JSON RPC code is here.

Written in C function like fashion as this lends itself to the error
checking and parse checking.  
"""


from traceback import format_exc
from traceback import format_exception_only
import urllib.parse
import base64
import re
import json
import socket

from magcode.core.globals_ import *
from magcode.core.wsgi import wsgi_outer_error

jsonrpc_request_types = ('application/json-rpc', 'application/json',
                        'application/json-request')
jsonrpc_response_types = ('application/json-rpc', 'application/json',
                        'application/json-request')

JSONRPC_PARSE_ERROR = -32700
JSONRPC_INVALID_REQUEST = -32600
JSONRPC_METHOD_NOT_FOUND = -32601
JSONRPC_INVALID_PARAMS = -32602
JSONRPC_INTERNAL_ERROR = -32603

jsonrpc_errors = {
        JSONRPC_PARSE_ERROR: "Parse error",
        JSONRPC_INVALID_REQUEST: "Invalid Request",
        JSONRPC_METHOD_NOT_FOUND: "Method not found",
        JSONRPC_INVALID_PARAMS: "Invalid params",
        JSONRPC_INTERNAL_ERROR: "Internal error",
    }

class BaseJsonRpcError(Exception):
    """
    Base JSON RPC Error Exception

    JSONRPC Error: JSONRPC_INTERNAL_ERROR
    """
    def __init__(self, *args):
        # Only initialise data if it has not been set up already....
        if not hasattr(self, 'data'):
            self.data = {}
        # Same for jsonrpc_error
        if not hasattr(self, 'jsonrpc_error'):
            self.jsonrpc_error = JSONRPC_INTERNAL_ERROR
        if (not len(args)):
            Exception.__init__(self, "Generic JSON RPC Error")
        else:
            Exception.__init__(self, *args)

class ParseErrorJsonRpcError(BaseJsonRpcError):
    """
    Parse Error JSON RPC exception

    JSONRPC Error:  JSONRPC_PARSE_ERROR
    """
    def __init__(self, message):
        if not message:
            message = jsonrpc_errors[JSONRPC_PARSE_ERROR]
        super().__init__(message)
        self.jsonrpc_error = JSONRPC_PARSE_ERROR

class InvalidParamsJsonRpcError(BaseJsonRpcError):
    """
    Invalid params JSON RPC exception

    JSONRPC Error:  JSONRPC_INVALID_REQUEST
    """
    def __init__(self, message):
        if not message:
            message = jsonrpc_errors[JSONRPC_INVALID_PARAMS]
        super().__init__(message)
        self.jsonrpc_error = JSONRPC_INVALID_PARAMS

class MethodNotFoundJsonRpcError(BaseJsonRpcError):
    """
    Method Not Found JSON RPC exception

    JSONRPC Error:  JSONRPC_METHOD_NOT_FOUND
    """
    def __init__(self, message):
        if not message:
            message = jsonrpc_errors[JSONRPC_METHOD_NOT_FOUND]
        super().__init__(message)
        self.jsonrpc_error = JSONRPC_METHOD_NOT_FOUND

class InvalidParamsJsonRpcError(BaseJsonRpcError):
    """
    Invalid Parameters JSON RPC exception

    JSONRPC Error:  JSONRPC_INVALID_PARAMS
    """
    def __init__(self, message):
        if not message:
            message = jsonrpc_errors[JSONRPC_INVALID_PARAMS]
        super().__init__(message)
        self.jsonrpc_error = JSONRPC_INVALID_PARAMS

class InternalErrorJsonRpcError(BaseJsonRpcError):
    """
    Internal Error JSON RPC exception

    JSONRPC Error:  JSONRPC_INTERNAL_ERROR
    """
    def __init__(self, message):
        if not message:
            message = jsonrpc_errors[JSONRPC_INTERNAL_ERROR]
        super().__init__(message)
        self.jsonrpc_error = JSONRPC_INTERNAL_ERROR

class WsgiJsonRpcServer(object):
    """
    Class for WSGI JSON RPC server functionality
    """
    def __init__(self, jsonrpc_application):
        """
        Instaniate WSGI application object
        """
        self.jsonrpc_application = jsonrpc_application

    def jsonrpc_single_error(self, environ, start_response, error, message,
            http_status = '200 OK', id_=None, data=None, exc_info=None):
        # log it
        log_error("[client %s] - JSON Error '%s', %s" 
                    % (environ['REMOTE_ADDR'], error, message))
        # form response and send it
        start_response(http_status, [('Content-type',
                        jsonrpc_response_types[0])], exc_info)
        response = {'jsonrpc': '2.0', 'id': id_, 'error': error, 
                'message': message}
        # Add data if given
        if data:
            response['data'] = data
        output = json.dumps(response).encode('iso-8859-1')
        return [output]

    def check_request_format(self, environ, start_response, request):
        """
        Check format of JSON request.  Returns JSON error if it fails
        """
        # Check that only labels 'jsonrpc', 'method', 'id', 'params' occur.
        valid_labels = set(['jsonrpc', 'method', 'id', 'params'])
        min_valid_labels = set(['method'])
        request_labels = set(list(request.keys()))
        if not (request_labels <= valid_labels 
                    and request_labels >= min_valid_labels):
            return self.jsonrpc_single_error(environ, start_response,
                    error=JSONRPC_INVALID_REQUEST, 
                    message=(jsonrpc_errors[JSONRPC_INVALID_REQUEST]
                            +' - request contains non-JSON RPC labels.'))
        method_thing = request['method']
        re_string = r'^[a-zA-Z0-9][._a-zA-Z0-9]*$'
        if not re.search(re_string, method_thing):
            return self.jsonrpc_single_error(environ, start_response,
                    error=JSONRPC_INVALID_REQUEST, 
                    message=(jsonrpc_errors[JSONRPC_INVALID_REQUEST]
                        +" - method name must consist of '%s'."
                            % re_string))

        rpc_version = request.get('jsonrpc')
        if rpc_version:
            if rpc_version not in ('1.0', '1.2', '2.0'):
                return self.jsonrpc_single_error(environ, start_response,
                        error=JSONRPC_INVALID_REQUEST, 
                        message=(jsonrpc_errors[JSONRPC_INVALID_REQUEST]
                            +' - server only supports JSON RPC 1.0, 1.2, 2.0'))

        id_thing = request.get('id')
        if id_thing:
            if (not isinstance(id_thing, str) and not isinstance(id_thing, int) 
                and id_thing is not None):
                return self.jsonrpc_single_error(environ, start_response,
                        error=JSONRPC_INVALID_REQUEST, 
                        message=(jsonrpc_errors[JSONRPC_INVALID_REQUEST]
                                +' - id has an invalid value.'))

        params_thing = request.get('params')
        if params_thing:
            if (not isinstance(params_thing, list) 
                    and not isinstance(params_thing, dict)):
                return self.jsonrpc_single_error(environ, start_response,
                        error=JSONRPC_INVALID_REQUEST, 
                        message=(jsonrpc_errors[JSONRPC_INVALID_REQUEST]
                                +' - params value is not a structured object.'))
        return None


    def __call__(self, environ, start_response):
        """
        WSGI DMS application.  Implements JSON RPCv2.0.

        Python Instance __call__ method - can call object instance like a 
        function!!!
        """
        try:
            log_info("[client %s] started processing." % environ['REMOTE_ADDR'])

            get_flag = False
            if environ.get('REQUEST_METHOD') == 'GET':
                # Deal with a GET
                get_flag = True
                # Just do this for now....
                # There can be a whole raft of thorny issues...
                if not settings['jsonrpc_accept_get']:
                    return wsgi_outer_error(environ, start_response,
                            "405 - REQUEST_METHOD 'GET' Not Allowed")
            elif environ.get('REQUEST_METHOD') != 'POST':
                # Error, but don't try and print external content because 
                # of possible fomat specifier issues.
                return wsgi_outer_error(environ, start_response, 
                        "405 - REQUEST_METHOD Not Allowed")
            # Check Content-Type
            if not environ.get('CONTENT_TYPE'):
                return wsgi_outer_error(environ, start_response, 
                    '400 - Bad Request', 
                    'Please specify a Content-type from %s.'
                        % str(jsonrpc_request_types))
            if (environ['CONTENT_TYPE'].split(';', 1)[0] 
                    not in jsonrpc_request_types):
                return wsgi_outer_error(environ, start_response, 
                    '400 - Bad Request', 'Content-type must be one of %s.'
                        % str(jsonrpc_request_types))

            # Decode request information
            if get_flag:
                # Deal with a GET - this won't be that reliable I guess...
                if not environ.get('QUERY_STRING'):
                    return self.jsonrpc_single_error(environ, start_response,
                            error=JSONRPC_PARSE_ERROR, 
                            message=jsonrpc_errors[JSONRPC_PARSE_ERROR] 
                                    + ' - no URL query string')
                try:
                    requests = urllib.parse.parse_qs(environ['QUERY_STRING'],
                                strict_parsing=True, errors='strict')
                    params = requests.get('params')
                    if params:
                        # Base64 Decode any parameters
                        requests['params'] = base64.urlsafe_b64decode(params)
                except Exception as exc:
                    return self.jsonrpc_single_error(environ, start_response,
                            error=JSONRPC_PARSE_ERROR, 
                            message=jsonrpc_errors[JSONRPC_PARSE_ERROR],
                            data={'exception_message': str_exc(exc),
                                'stack_trace': format_exc()})
            else:
                # Deal with a POST
                # 1st, get and check 'Content-length'
                # Check Content-length
                try:
                    content_length = environ.get('CONTENT_LENGTH')
                    content_length = int(content_length)
                except (ValueError, TypeError):
                    return wsgi_outer_error(environ, start_response, 
                        '400 - Bad Request', 
                        'Please specify a valid Content-length.')

                if content_length > settings['jsonrpc_max_content_length']:
                    return wsgi_outer_error(environ, start_response, 
                        '400 - Bad Request', 
                        'Content-length must be less than %s bytes.'
                        % settings['jsonrpc_max_content_length'] )

                # Read in body, and check for errors
                try:
                    request_body = environ['wsgi.input'].read(content_length)
                except (KeyError, socket.error, IOError) as exc:
                    # Something has gone really wrong on the server.
                    log_warn ("Web server disconnected? - %s.", str(exc))
                    return [] 

                # Decode request JSON - if error do an HTTP status error
                # response!
                try:
                    requests = json.loads(request_body.decode('iso-8859-1'))
                except ValueError as exc:
                    return self.jsonrpc_single_error(environ, start_response,
                            error=JSONRPC_PARSE_ERROR, 
                            message=jsonrpc_errors[JSONRPC_PARSE_ERROR],
                            data={'exception_message': str_exc(exc),
                                'stack_trace': format_exc()})

            # We now have something that definitely looks like JSON.
            # Check format of request for JSON RPC request form
            if isinstance(requests, list):
                request_batch = True
            elif isinstance(requests, dict):
                request_batch = False
                requests = [requests]
            else:
                return self.jsonrpc_single_error(environ, start_response,
                        error=JSONRPC_INVALID_REQUEST, 
                        message=(jsonrpc_errors[JSONRPC_INVALID_REQUEST]
                            +' - request not a JSON object or array as required.'))

            # Check requests for format validity - any syntax errors
            # result in complete failure - out of spec stuff could be due
            # to random bit flipping (even happens with TCP checksum, 1 bit
            # one way, 1 other bit flip canceling the error..
            for request in requests:
                result = self.check_request_format(environ,
                                start_response, request)
                if result:
                        return result

            # Call DMS wsgi URL specific code
            try:
                response = self.jsonrpc_application(environ, start_response,
                                                    requests)
            except BaseJsonRpcError as exc:
                data = exc.data
                data.update({'exception_message': str_exc(exc),
                                'exception_type': str_exc_type(exc)})
                if jsonrpc_error_stack_trace():
                    data['stack_trace'] = format_exc()
                return self.jsonrpc_single_error(environ, start_response,
                        error = exc.jsonrpc_error,
                        message = str(exc),
                        data = data)
            
            if request_batch and len(response) == 0:
                # batch was just a bunch of notifications
                response = ''
            elif not request_batch:
                response = response[0]

            status = b'200 OK'
            content_type = jsonrpc_request_types[0]
            if response:
                response = json.dumps(response).encode('iso-8859-1')
                response_headers = [('Content-type', content_type),
                                    ('Content-Length', str(len(response)))]
            else:
                response = ''
            start_response(status, response_headers)
            return [response]
        finally:
            log_info("[client %s] finished processing."
                    % environ['REMOTE_ADDR'])

# Helper functions for exceptions
def jsonrpc_error_stack_trace():
    if settings['jsonrpc_error_stack_trace']:
        return(str(settings['jsonrpc_error_stack_trace']).lower() 
                        in ('true', 'on', 'yes', '1'))
    else:
        return False

def str_exc_type(exc):
    """
    return exception inheritance tree as a class string
    """
    def _tree_walk(class_):
        nonlocal tree
        if not tree:
            tree = class_.__name__
        else:
            tree = class_.__name__ + '.' + tree
        if class_.__name__ == BaseJsonRpcError.__name__:
            return
        _tree_walk(class_.__bases__[0])

    tree = ''
    if not isinstance(exc, type):
        exc = exc.__class__
    _tree_walk(exc)
    return tree

