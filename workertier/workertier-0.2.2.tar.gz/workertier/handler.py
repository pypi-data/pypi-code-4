#coding:utf-8
from gevent import monkey
from workertier.backends import InvalidKey, BackendUnavailable

monkey.patch_all()


class Handler(object):
    def __init__(self, cache, dispatcher):
        self.cache = cache
        self.dispatcher = dispatcher

    def handle_request(self, env, start_response):
        method = env['REQUEST_METHOD']

        if method not in ("HEAD", "GET"):
            start_response("405 METHOD NOT ALLOWED", [])
            return

        url = env['PATH_INFO']

        if not url.startswith('/') or url == "/":
            start_response('404 Not Found', [])
            return

        key = url[1:]

        try:
            value = self.cache.get(key)
        except InvalidKey:
            start_response('400 Bad Request', [])
            return
        except BackendUnavailable:
            start_response('503 Service Unavailable', [])
            return

        if value is None:
            start_response('203 Non-Authoritative Information', [])
            self.dispatcher.dispatch(key)
            return

        start_response('200 OK', [('Content-Type', 'text/plain')])
        yield value
        yield "\n"
