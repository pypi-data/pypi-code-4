#!/usr/bin/env python

# Copyright (c) 2011-2012 Ben Croston
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from uuid import uuid4
from urlparse import urlparse
import json
import httplib
import copy
import socket
import hashlib

def _encrypt_password(password):
    return hashlib.md5(password.encode()).hexdigest() if password is not None else None

class _Method(object):
    def __init__(self, call, name, username=None, password=None):
        self.call = call
        self.name = name
        self._username = username
        self._password = password

    def __call__(self, *args, **kwargs):
        request = {}
        request['id'] = str(uuid4())
        request['method'] = self.name

        if len(args) > 0 and len(kwargs) > 0:
            raise JSONRPCProtocolError('Cannot use both positional and keyword arguments.')

        if len(args) > 0:
            params = copy.copy(args)
        elif len(kwargs) > 0:
            params = copy.copy(kwargs)
        else:
            params = None
        request['params'] = params

        if self._username is not None:
            request['username'] = self._username
        if self._password is not None:
            request['password'] = _encrypt_password(self._password)

        if request['method'] == '__getfile__':
            return self.call(json.dumps(request), generator=True)

        resp = self.call(json.dumps(request))
        if resp is None:
            raise JSONRPCProtocolError('Server response is None')
        resp = json.loads(resp.decode())
        if resp['id'] != request['id']:
            raise JSONRPCProtocolError('Inconsistent JSON request id returned')
        if resp['error'] is not None:
            raise RemoteException(resp['error']['error'])  ## btc fixme - also pass exception type (e.g. IntegrityError)

        return resp['result']

    def __getattr__(self, name):
        return _Method(self.call, "%s.%s" % (self.name, name), self._username, self._password)

class _JSONRPCTransport(object):
    headers = {'Content-Type':'application/json',
               'Accept':'application/json'}

    def __init__(self, uri, proxy_uri=None, user_agent=None):
        self.headers['User-Agent'] = user_agent if user_agent is not None else 'AuthRPC'
        if proxy_uri is not None:
            self.connection_url = urlparse(proxy_uri)
            self.request_path = uri
        else:
            self.connection_url = urlparse(uri)
            self.request_path = self.connection_url.path
            
    def request(self, request_body):
        if self.connection_url.scheme == 'http':
            if self.connection_url.port is None:
                port = 80
            else:
                port = self.connection_url.port
            connection = httplib.HTTPConnection(self.connection_url.hostname+':'+str(port))
        elif self.connection_url.scheme == 'https':
            if self.connection_url.port is None:
                port = 443
            else:
                port = self.connection_url.port
            connection = httplib.HTTPSConnection(self.connection_url.hostname+':'+str(port))
        else:
            raise Exception('unsupported transport')
        connection.request('POST', self.request_path, body=request_body, headers=self.headers)
        return connection.getresponse()

class BadRequestError(Exception):
    """HTTP 400 - Bad Request"""
    def __init__(self, msg=''):
        Exception.__init__(self,'HTTP 400 - Bad Request\n%s'%msg)

class UnauthorisedError(Exception):
    """HTTP 401 - Unauthorised"""
    def __init__(self):
        Exception.__init__(self,'HTTP 401 - Unauthorised')

class ForbiddenError(Exception):
    """HTTP 403 - Forbidden"""
    def __init__(self):
        Exception.__init__(self,'HTTP 403 - Forbidden')

class NotFoundError(Exception):
    """HTTP 404 - Not Found"""
    def __init__(self):
        Exception.__init__(self,'HTTP 404 - Not Found')

class BadGatewayError(Exception):
    """HTTP 502 - Bad Gateway"""
    def __init__(self):
        Exception.__init__(self,'HTTP 502 - Bad Gateway')

class InternalServerError(Exception):
    """HTTP 500 - Internal Server Error"""
    def __init__(self):
        Exception.__init__(self,'HTTP 500 - Internal Server Error')

class NetworkSocketError(Exception):
    pass

class JSONRPCProtocolError(Exception):
    """Raised when the JSONRPC protocol has been broken"""
    pass

class RemoteException(Exception):
    """Raised when there is an exception raised on the server"""
    pass

class ServerProxy(object):
    """
    A client class to communicate with a AuthRPC server
    """
    def __init__(self, uri, proxy_uri=None, user_agent=None, username=None, password=None):
        """
        uri        - the URI of a corresponding AuthRPC server
        proxy_uri  - the http proxy to use, if any
        user_agent - user agent to be used (can be used as part of authentication)
        username   - username to use in requests
        password   - password to use in requests
        """
        assert uri is not None
        self.__transport = _JSONRPCTransport(uri, proxy_uri=proxy_uri, user_agent=user_agent)
        self._username = username
        self._password = password

    def _response_generator(self, response):
        while True:
            data = response.read(262144) # 262144 == 256k
            if not data:
                break
            yield data

    def _request(self, request, generator=False):
        # call a method on the remote server
        try:
            response = self.__transport.request(request)
        except socket.error:
            raise NetworkSocketError
        if response.status == 200:
            if generator:
                return self._response_generator(response)
            else:
                return response.read()
        elif response.status == 400:
            raise BadRequestError(response.read().decode())
        elif response.status == 401:
            raise UnauthorisedError
        elif response.status == 403:
            raise ForbiddenError
        elif response.status == 404:
            raise NotFoundError
        elif response.status == 500:
            raise InternalServerError
        elif response.status == 502:
            raise BadGatewayError
        else:
            raise Exception('HTTP Status %s'%response.status)

    def __repr__(self):
        return "<ServerProxy for %s%s>" %(self.__host, self.__handler)

    __str__ = __repr__

    def __getattr__(self, name):
        # magic method dispatcher
        return _Method(self._request, name, self._username, self._password)

################# batch calls vvv

class _BatchMethod(object):
    def __init__(self, name):
        self.name = name
        self.request = {}

    @property
    def id(self):
        return self.request['id']

    def __call__(self, *args, **kwargs):
        self.request = {}
        self.request['method'] = self.name
        self.request['id'] = str(uuid4())
        if len(args) > 0 and len(kwargs) > 0:
            raise JSONRPCProtocolError('Cannot use both positional and keyword arguments.')
        if len(args) > 0:
            self.request['params'] = copy.copy(args)
        elif len(kwargs) > 0:
            self.request['params'] = copy.copy(kwargs)
        else:
            self.request['params'] = None

    def __getattr__(self, name):
         new_name = '%s.%s' % (self.name, name)
         self.name = new_name
         return self

    def __repr__(self):
        return json.dumps(self.request)

    __str__ = __repr__

class BatchCall(object):
    """
    A class to place a batch of requests in one call
    """
    def __init__(self, serverproxy):
        self._server = serverproxy
        self._queue = []

    def __getattr__(self, name):
        """Add the call to the queue"""
        method = _BatchMethod(name)
        self._queue.append(method)
        return method

    def __call__(self):
        """Process the queue"""
        requests = []
        if len(self._queue) < 1:
            # no calls have been added to batch
            return

        req = [self._server._username, _encrypt_password(self._server._password)]
        req = json.dumps(req)
        req = req[:-1]    # strip trailing ']'
        req += ', '
        req += ', '.join(str(q) for q in self._queue)
        req += ']'

        response = json.loads(self._server._request(req).decode())

        # catch error in auth
        if type(response) == dict and response['error'] is not None:
            raise RemoteException(response['error']['error'])  ## btc fixme - also pass exception type (e.g. IntegrityError)

        result = []
        for i,r in enumerate(response):
            if r['id'] != self._queue[i].id:
                raise JSONRPCProtocolError('Inconsistent JSON request id returned')
            result.append(r['result'])

        # clear the queue
        self._queue = []

        return result

    def __repr__(self):
        return '<BatchCall for %s>' % self._server

    __str__ = __repr__

