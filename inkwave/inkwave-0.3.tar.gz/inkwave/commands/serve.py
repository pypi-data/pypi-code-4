import logging
import os
import filespy
from webob import (
    Request,
    Response,
)
from webob.exc import HTTPNotFound
from wsgiref.simple_server import (
    WSGIServer,
    WSGIRequestHandler,
)
from cliff.command import Command
from inkwave.core import env
from inkwave.errors import RouteNotFound


class HttpServer(WSGIServer):
    def __init__(self, *args, **kwargs):
        super(HttpServer, self).__init__(*args, **kwargs)
        self.dir_snapshot = {}

    def service_actions(self):
        s = filespy.make_snapshot(env.root)
        #print(list(filespy.snapshot_diff(self.dir_snapshot, s)))
        self.dir_snapshot = s


class WsgiApp:
    def __init__(self):
        pass

    def __call__(self, environ, start_response):
        req = Request(environ)
        try:
            content_type, enc, data = env.resources.dispatch('get', req.path)
            resp = Response(data)
            resp.content_type = content_type
        except RouteNotFound:
            resp = HTTPNotFound()
        return resp(environ, start_response)


class Serve(Command):
    "Launch development server"

    site = True
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Serve, self).get_parser(prog_name)
        parser.add_argument('--address',
                            help='Address [DEFAULT: 127.0.0.1]')
        parser.add_argument('--port', type=int,
                            help='Port number [DEFAULT: 8000]')
        return parser

    def take_action(self, args):
        env.init_db()
        self.log.info("Starting HTTP server ({}:{})"
                      .format(env.address, env.port))
        os.chdir(env.out)
        try:
            wsgi_app = WsgiApp()
            server = HttpServer((env.address, env.port), WSGIRequestHandler)
            server.set_app(wsgi_app)
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        self.log.info("Stopping HTTP server")
