import unittest
from dingus import Dingus
from webtest import TestApp
from objgraph_middleware import (ObjgraphMiddleware,
                                 FlaskObjgraphMiddleware,
                                 PyramidObjgraphMiddleware)


class ObjgraphMiddlewareTestBase(unittest.TestCase):

    def simple_view(self):
        return 'Hello world!'

    view = simple_view

    def simple_app(self, environ, start_response):
        """Simplest possible application object"""
        status = '200 OK'
        response_headers = [('Content-type', 'text/plain')]
        start_response(status, response_headers)
        return [self.view()]

    factory = ObjgraphMiddleware

    def log(self, data):
        self.logs.append(data)

    def setUp(self):
        self.logs = []
        self.middleware = self.factory(self.simple_app, sampling_rate=1.0)
        self.middleware.recordSample = self.log
        self.app = TestApp(self.middleware)

    def tearDown(self):
        self.view = self.simple_view
        self.logs = []


class Leak(object):
    """An object to be leaked"""


LEAKS = []


class TestObjgraphMiddleware(ObjgraphMiddlewareTestBase):

    def leaky_view(self):
        LEAKS.append([Leak() for leak in range(10)])
        return 'Leaky view'

    def test_catches_leak(self):
        self.view = self.leaky_view
        self.assertEquals(self.app.get('/').body, 'Leaky view')
        self.assertEquals(len(self.logs), 1) # was called only once
        self.assertEquals(self.logs[0]['growth_stats']['Leak'], 10)

    def test_no_leak(self):
        self.assertEquals(self.app.get('/').body, 'Hello world!')
        self.assertEquals(len(self.logs), 1) # was called only once
        self.assertEquals(self.logs[0]['growth_stats'],
                          {'IteratorWrapper': 1, 'TestResponse': 1, 'dict': 1})

    def test_exception(self):
        self.middleware.getMetadata = 'Not Callable'
        self.assertEquals(self.app.get('/').body, 'Hello world!')
        self.assertEquals(len(self.logs), 0) # was not called at all

    def test_logs_metadata(self):
        self.middleware.getMetadata = lambda environ: {'metadata': 'is cool'}
        self.assertEquals(self.app.get('/').body, 'Hello world!')
        self.assertEquals(len(self.logs), 1) # was called only once
        self.assertEquals(self.logs[0]['metadata'], 'is cool')


class TestFlaskObjgraphMiddleware(ObjgraphMiddlewareTestBase):

    factory = FlaskObjgraphMiddleware

    def test_getMetadata(self):
        """getMetadata returns whatever is returned by parseUrl"""
        self.middleware.parseUrl = lambda environ: (environ['endpoint'], environ['args'])
        metadata = self.middleware.getMetadata({'endpoint': 'hello', 'args': 'world'})
        self.assertEquals(metadata, {'endpoint': 'hello', 'args': 'world'})


class TestPyramidObjgraphMiddleware(ObjgraphMiddlewareTestBase):

    factory = PyramidObjgraphMiddleware

    def test_getMetadata(self):
        self.assertEquals(self.middleware.getMetadata({}),
                          {'endpoint': ''})
        route = Dingus()
        self.assertEquals(self.middleware.getMetadata({'bfg.routes.route': route}),
                          {'endpoint': route.name})
