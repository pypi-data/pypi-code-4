
import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import sys; sys.path.insert(0, '.')
from gevent import monkey; monkey.patch_all()
from socketio import socketio_manage
from socketio.server import SocketIOServer
from django.conf import settings
from threading import Lock
from django.core.handlers.wsgi import WSGIRequest, WSGIHandler
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from socketio.handler import SocketIOHandler
from socketio.policyserver import FlashPolicyServer
from django.utils.importlib import import_module
from utils import import_class
lock = Lock()


def not_found(start_response):
    print "not found"
    start_response('404 Not Found', [])
    return ['<h1>Not Found</h1>']


class Application(object):
    _my_namespaces = {}

    def __init__(self, namespaces):
        self._my_namespaces = namespaces
        super(Application, self).__init__()
        self.middleware = [
            SessionMiddleware(),
            AuthenticationMiddleware()
        ]
        self.django_wsgi = WSGIHandler()

    def __call__(self, environ, start_response):
        path = environ['PATH_INFO']
        print
        print "-" * 20

        if path.startswith('/socket.io/static/'):
            try:
                filename = os.path.join(settings.STATIC_ROOT, path.replace("/socket.io/static/", ""))
                data = open(filename).read()
            except Exception, ex:
                print ex
                return not_found(start_response)

            if path.endswith(".js"):
                content_type = "text/javascript"
            elif path.endswith(".css"):
                content_type = "text/css"
            elif path.endswith(".swf"):
                content_type = "application/x-shockwave-flash"
            else:
                content_type = "text/html"

            start_response('200 OK', [('Content-Type', content_type)])
            return [data]

        if "socketio" not in environ:
            return self.django_wsgi(environ, start_response)
        else:
            request = WSGIRequest(environ)
            for middle in self.middleware:
                middle.process_request(request)
            socketio_manage(environ, self._my_namespaces, request=request)


class CrossOriginSocketIOHandler(SocketIOHandler):

    def write_plain_result(self, data):
        self.start_response("200 OK", [
            ("Content-Type", "text/plain"),
            ("Access-Control-Allow-Origin", self.environ.get('HTTP_ORIGIN', '*')),
            ("Access-Control-Allow-Credentials", "true"),
            ("Access-Control-Allow-Methods", "POST, GET, OPTIONS"),
            ("Access-Control-Max-Age", 3600),
            ("Content-Type", "text/plain"),
        ])
        self.result = [data]


class CrossOriginSocketIOServer(SocketIOServer):

    def __init__(self, *args, **kwargs):
        self.sockets = {}
        if 'resource' in kwargs:
            print "DEPRECATION WARNING: use `namespace` instead of `resource`"
        self.namespace = kwargs.pop('resource', kwargs.pop('namespace',
                                                           'socket.io'))
        self.transports = kwargs.pop('transports', None)

        if kwargs.pop('policy_server', True):
            self.policy_server = FlashPolicyServer()
        else:
            self.policy_server = None

        kwargs['handler_class'] = CrossOriginSocketIOHandler
        super(SocketIOServer, self).__init__(*args, **kwargs)


def serve(settings):
    host = settings.HOST
    port = settings.PORT
    print 'Listening on %s:%s' % (settings.HOST, settings.PORT)

    data = {}

    keyfile = getattr(settings, "KEYFILE", None)
    certfile = getattr(settings, "CERTFILE", None)
    if keyfile and certfile:
        data.update(dict(
            keyfile=keyfile,
            certfile=certfile
        ))

    app_module = getattr(settings, "APPLICATION", None)
    if not app_module:
        app = Application(settings.NAMESPACES)
    else:
        app = import_class(app_module)(settings.NAMESPACES)

    CrossOriginSocketIOServer((host, port), app,
        policy_server=False, **data).serve_forever()

if __name__ == "__main__":
    import socketio_settings
    serve("0.0.0.0", socketio_settings)  # sslwrap_simple()
