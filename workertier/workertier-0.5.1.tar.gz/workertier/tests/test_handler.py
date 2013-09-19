#!/usr/bin/env python
#coding:utf-8
import unittest

from workertier.handler import Handler
from workertier.backends import InvalidKey, BackendUnavailable


class HandlerTestCase(unittest.TestCase):
    def setUp(self):
        self.response_code = self.reason = self.headers = None

        def start_response(status_line, headers):
            self.response_code, self.reason = status_line.split(' ', 1)
            self.response_code = int(self.response_code)
            self.headers = headers

        self._start_response = start_response

    def test_method_not_allowed(self):
        handler = Handler(None, None)
        for method in ("OPTIONS", "POST", "PUT", "DELETE", "TRACE"):
            list(handler.handle_request({"REQUEST_METHOD": method, "PATH_INFO":"/key"}, self._start_response))
            # List it: it's a generator
            self.assertEqual(405, self.response_code)

    def test_invalid_url(self):
        handler = Handler(None, None)
        for url in ("/", "blah", ""):
            env = {"REQUEST_METHOD": "GET", "PATH_INFO": url}
            list(handler.handle_request(env, self._start_response))
            self.assertEqual(404, self.response_code)

    def test_backend_errors(self):
        class FailingBackend(object):
            def __init__(self, exc_class):
                self.exc_class = exc_class
            def get(self, key):
                raise self.exc_class()
            dispatch = get

        class WorkingBackend(object):
            def get(self, key):
                return None
            def dispatch(self, key):
                pass

        # Test the two exceptions
        for response_code, failing_backend in ((400, FailingBackend(InvalidKey)), (503, FailingBackend(BackendUnavailable))):
            env = {"REQUEST_METHOD": "GET", "PATH_INFO": "/key"}

            # We can only test for the cache: the message queue is asynchronous
            handler = Handler(failing_backend, WorkingBackend())
            list(handler.handle_request(env, self._start_response))
            self.assertEqual(response_code, self.response_code)

    def test_working_backend(self):
        class Cache(object):
            def __init__(self, ret):
                self.ret = ret
                self.called_with = None

            def get(self, key):
                self.called_with = key
                return self.ret

        class Dispatcher(object):
            def __init__(self):
                self.called_with = None

            def dispatch(self, key):
                self.called_with = key

        env = {"REQUEST_METHOD": "GET", "PATH_INFO": "/key"}

        cache, dispatcher = Cache(None), Dispatcher()
        handler = Handler(cache, dispatcher)
        list(handler.handle_request(env, self._start_response))

        self.assertEqual(203, self.response_code)
        self.assertEqual("key", cache.called_with)
        self.assertEqual("key", dispatcher.called_with)

        cache, dispatcher = Cache("value"), Dispatcher()
        handler = Handler(cache, dispatcher)
        output = list(handler.handle_request(env, self._start_response))

        self.assertEqual(200, self.response_code)
        self.assertEqual("key", cache.called_with)
        self.assertEqual(None, dispatcher.called_with)
        self.assertEqual(["value", "\n"], output)




