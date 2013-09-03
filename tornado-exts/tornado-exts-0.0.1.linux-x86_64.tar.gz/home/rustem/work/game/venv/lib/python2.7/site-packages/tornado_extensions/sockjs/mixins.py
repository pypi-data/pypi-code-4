import simplejson as json
from tornado import gen
from importlib import import_module
from settings import settings as global_settings


class groupped_emits(object):
    """Allows to send several emits in group.
    """

    def __init__(self, conn):
        self.conn = conn

    def __enter__(self):
        self.conn._group_emits = True
        self.conn._emit_queue = []

    def __exit__(self, etype, value, traceback):
        if etype is not None:
            return False
        self.conn.flush_emits()
        return True


class EmitMixin(object):
    r"""EmitMixin is a mixin that helps to send message to client socket
    according to comet protocol."""

    def flush_emits(self):
        """Sends all preserved emits in one send"""
        self._group_emits = False
        if self._emit_queue:
            self.send(json.dumps([{
                'name': name, 'args': args}
                for name, args in self._emit_queue
            ]))
        self._emit_queue = []

    def emit(self, event, *args):
        r"""Emits a specific message to a socket. According to the message
        type `event`, it will be handled appropriately on client side.

        Parameters
        ----------
        event : str
            type of message
        args : list
            arguments that represent a message body

        Extended summary
        ----------------
        send() : SockJSConnection method to send messages to client socket
        """
        if hasattr(self, '_group_emits') and self._group_emits:
            self._emit_queue.append((event, args))
        else:
            self.send(json.dumps({
                'name': event,
                'args': args
            }))


class BroadcastMixin(object):
    r"""BroadcastMixin is a mixin that helps to send message to set of client
     sockets according to comet protocol."""

    def emit_broadcast(self, clients, event, *args):
        r"""Emits a message to set of clients.

        Parameters
        ----------
        clients : set or list
            unique socket instances to whom msg will be broadcasted
        event : str
            type of message
        args : list
            arguments that represent a message body

        Extended summary
        ----------------
        broadcast() : SockJSConnection method to send message to set of sockets.
        Read more about it in `SockJS documentation <http://goo.gl/B1PWG>`_.
        """
        if not isinstance(clients, list):
            clients = list(clients)
        self.broadcast(clients, json.dumps({
            'name': event,
            'args': args
        }))

    def msg_broadcast(self, clients, ms, *args):
        r"""Sends chat | feed | notification message to client-side. Depending
        on `ms` parameter corresponding event handler will be executed.

        Parameters
        ----------
        clients : set or list
        ms : str
            message source (chat | feed | notification)
        args : list
            arguments that represent a message body

        Notes
        -----
        `emit_broadcast()` function is used
        """
        self.emit_broadcast(clients, '{}Message'.format(ms), *args)

    def exception_msg(self, ex_type):
        r"""Sends an exception to client of particular type.

        Parameters
        ----------
        ex_type : str
        """
        self.send(json.dumps({
                'name': 'exception',
                'args': [{'type': ex_type}]
            }))


class SettingsMixin(object):

    @property
    def settings(self):
        return global_settings


class MiddlewaresMixin(SettingsMixin):

    @property
    def middlewares(self):
        return self.__class__._middlewares

    @middlewares.setter
    def middlewares(self, value):
        self.__class__._middlewares = value

    def _init_middlewares(self):
        settings = self.settings
        middlwares_list = settings.get('websocket_middlewares', None) or []
        result = []
        for path in middlwares_list:
            path, cls_name = path.rsplit('.', 1)
            cls = getattr(import_module(path), cls_name)
            result.append(cls(settings))

        self.middlewares = result

    @gen.engine
    def on_open(self, request):
        # obj.on_open(self, request, callback=self.on_open_callback)
        if self.middlewares is None:
            self._init_middlewares()
        for obj in self.middlewares:
            if hasattr(obj, 'on_open') and callable(obj.on_open):
                obj.on_open(self, request)
            if hasattr(obj, 'on_open_async') and callable(obj.on_open_async):
                yield gen.Task(obj.on_open_async, self, request)

        if hasattr(self, 'on_openm'):
            self.on_openm(request)

    # def on_close(self):
    #     super(MiddlewaresMixin, self).on_close()
    #     if self.middlewares is None:
    #         self._init_middlewares()
    #     for obj in self.middlewares:
    #         if hasattr(obj, 'on_close') and callable(obj.on_close):
    #             obj.on_close(self)
