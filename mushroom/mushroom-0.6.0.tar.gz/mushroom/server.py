from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler


class Server(WSGIServer):

    def __init__(self, listener, *args, **kwargs):
        kwargs.setdefault('handler_class', WebSocketHandler)
        super(Server, self).__init__(listener, *args, **kwargs)

    @property
    def sessions(self):
        return self.application.sessions
