#coding:utf-8
from workertier.backends import InvalidKey, BackendUnavailable


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
            # Note: This wouldn't make sense for an HA app, but we're just trying to do a POC here,
            # so we'll appreciate the debug info in case our dispatcher dies.
            if value is None:
                self.dispatcher.dispatch(key)
        except InvalidKey:
            start_response('400 Bad Request', [])
            return
        except BackendUnavailable:
            start_response('503 Service Unavailable', [])
            return

        if value is None:
            start_response('203 Non-Authoritative Information', [])
            return

        start_response('200 OK', [('Content-Type', 'text/plain')])
        yield value
        yield "\n"
