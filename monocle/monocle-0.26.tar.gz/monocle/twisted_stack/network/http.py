# -*- coding: utf-8 -*-
#
# by Steven Hazel

import urlparse
import logging

from monocle import _o, Return, VERSION, launch, log_exception
from monocle.callback import Callback
from monocle.stack.network.http import HttpHeaders, HttpResponse, HttpRouter, write_request, read_response, extract_response
from monocle.twisted_stack.eventloop import reactor
from monocle.twisted_stack.network import Service, SSLService, Client, SSLClient

from twisted.internet import ssl
from twisted.internet.protocol import ClientCreator
from twisted.web import server, resource

log = logging.getLogger("monocle.twisted_stack.network.http")

class HttpException(Exception): pass


class _HttpServerResource(resource.Resource):
    isLeaf = 1

    def __init__(self, handler):
        self.handler = handler

    def render(self, request):
        @_o
        def _handler(request):
            try:
                value = yield self.handler(request)
                code, headers, content = extract_response(value)
            except Exception:
                log_exception()
                code, headers, content = 500, {}, "500 Internal Server Error"
            try:
                if request._disconnected:
                    return

                request.setResponseCode(code)
                headers.setdefault('Server', 'monocle/%s' % VERSION)
                grouped_headers = {}
                for name, value in headers.iteritems():
                    if name in grouped_headers:
                        grouped_headers[name].append(value)
                    else:
                        grouped_headers[name] = [value]
                for name, value in grouped_headers.iteritems():
                    request.responseHeaders.setRawHeaders(name, value)
                request.write(content)

                # close connections with a 'close' header
                if headers.get('Connection', '').lower() == 'close':
                    request.channel.persistent = False

                request.finish()
            except Exception:
                log_exception()
                raise
        _handler(request)
        return server.NOT_DONE_YET


class HttpServer(Service, HttpRouter):
    def __init__(self, port, handler=None, bindaddr="", backlog=128):
        HttpRouter.__init__(self)
        self.port = port
        self.handler = handler
        self.bindaddr = bindaddr
        self.backlog = backlog
        self._twisted_listening_port = None
        self.factory = server.Site(_HttpServerResource(self.handle_request))


class HttpsServer(SSLService, HttpRouter):
    def __init__(self, port, ssl_options, handler=None, bindaddr="", backlog=128):
        HttpRouter.__init__(self)
        self.port = port
        self.ssl_options = ssl_options
        self.handler = handler
        self.bindaddr = bindaddr
        self.backlog = backlog
        self._twisted_listening_port = None
        self.factory = server.Site(_HttpServerResource(self.handle_request))
