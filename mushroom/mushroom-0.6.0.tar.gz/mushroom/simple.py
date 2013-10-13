import codecs
import logging

from mushroom.application import Application
from mushroom.http import HttpResponse
from mushroom.rpc import MethodDispatcher
from mushroom.server import Server
from mushroom.session import SessionHandlerAdapter


class StaticFile(object):
    content_types = {
        'html': 'text/html',
        'txt': 'text/plain',
        'css': 'text/css',
        'js': 'text/javascript',
        'json': 'application/json',
        'jpg': 'image/jpeg',
        'png': 'image/png',
        'gif': 'image/gif',
        'ico': 'image/x-icon',
    }

    def __init__(self, filename):
        self.filename = filename
        try:
            name, extension = filename.rsplit('.', 1)
        except ValueError:
            self.content_type = 'application/octet-stream'
        else:
            self.content_type = self.content_types.get(extension,
                    'application/octet-stream')

    def load_file(self):
        with codecs.open(self.filename) as fh:
            return fh.read()

    def get(self, request):
        return HttpResponse('200 OK', self.load_file(),
                extra_headers={'Content-Type': self.content_type})


class SimpleApplication(Application):

    def __init__(self, urls=None, rpc_handler=None, session_handler=None):
        self.urls = urls or []
        super(SimpleApplication, self).__init__(rpc_handler, session_handler)

    def request(self, request):
        websocket = request.environ.get('wsgi.websocket')
        if request.method == 'GET' and not websocket:
            # FIXME The current mushroom version still uses a splitted
            # path which is not very pretty. When request.path is a normal
            # string again this code must be removed.
            request_path = '/' + '/'.join(request.path)
            for path, resource in self.urls:
                if request_path == path:
                    return resource.get(request)
            return HttpResponse('404 Not Found', '404 Not Found',
                    extra_headers={'Content-Type': 'text/plain'})
        return super(SimpleApplication, self).request(request)


class SimpleServer(Server):
    '''
    This is the preferred way of starting to work with mushroom.
    This server class makes it possible to use mushroom with only
    a few lines of code by relying on some defaults:

        - All RPC methods are prefixed with 'rpc_'
        - Session handlers calls are prefixed wit 'session_'
        - The server runs on localhost with port 39288

    In order to use this class create a subclass from it, overwrite
    the urls attribute and start `YourServer.main()`.
    '''
    urls = None
    host = '127.0.0.1'
    port = 39288 # picked by random.randint(1024, 65535)

    def __init__(self, listener, **kwargs):
        application = SimpleApplication(
                urls=self.urls,
                rpc_handler=MethodDispatcher(self, 'rpc_'),
                session_handler=SessionHandlerAdapter(self, 'session_'))
        super(SimpleServer, self).__init__(listener,
                application=application,
                **kwargs)
        self.server_init()

    def server_init(self):
        pass

    def session_authenticate(self, session, auth):
        return True

    def session_connect(self, session):
        pass

    def session_disconnect(self, session):
        pass

    @classmethod
    def main(cls):
        logging.basicConfig()
        listener = (cls.host, cls.port)
        print('Server running at http://%s:%d/' % listener)
        server = cls(listener)
        server.serve_forever()
