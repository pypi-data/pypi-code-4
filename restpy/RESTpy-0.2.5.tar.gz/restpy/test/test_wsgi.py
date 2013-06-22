from werkzeug.test import Client, EnvironBuilder
from werkzeug.wrappers import Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import MethodNotAllowed, BadRequest

import unittest
from StringIO import StringIO

from restpy.applications import RestApplication
from restpy.wrappers import Request
from restpy.wsgi import RequestMiddleware
from restpy.wsgi import ExceptionHandlerMiddleware
from restpy.wsgi import SerializationMiddleware


class TestEndpoint(object):

    def GET(self, request):

        return Response("TEST")

    def POST(self, request):

        raise BadRequest("TEST")

    def PUT(self, request):

        return Response(request.content)


test_ulrs = Map([
    Rule('/', endpoint=TestEndpoint)
])


class TestRequestMiddleware(unittest.TestCase):

    def setUp(self, *args, **kwargs):

        super(TestRequestMiddleware, self).setUp(*args, **kwargs)
        self.application = RequestMiddleware(RestApplication(test_ulrs))
        self.client = Client(self.application, Response)

    def test_wraps_requests(self):

        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, "TEST")


class TestExceptionHandlerMiddleware(unittest.TestCase):

    def setUp(self, *args, **kwargs):

        super(TestExceptionHandlerMiddleware, self).setUp(*args, **kwargs)
        self.application = RestApplication(test_ulrs)
        self.application = ExceptionHandlerMiddleware(self.application)

    def test_catches_method_exceptions(self):

        request = Request(EnvironBuilder(path='/',
                                         method='POST').get_environ())

        response = self.application(request)

        self.assertTrue(isinstance(response, BadRequest))

    def test_catches_routing_exceptions(self):

        request = Request(EnvironBuilder(path='/',
                                         method='DELETE').get_environ())

        response = self.application(request)

        self.assertTrue(isinstance(response, MethodNotAllowed))


class TestSerializationMiddleware(unittest.TestCase):

    def setUp(self, *args, **kwargs):

        super(TestSerializationMiddleware, self).setUp(*args, **kwargs)
        self.application = RestApplication(test_ulrs)
        self.application = SerializationMiddleware(self.application)

    def test_handles_json(self):

        data = '{"test": 1234}'
        request = Request(EnvironBuilder(path='/',
                                         method='PUT',
                                         input_stream=StringIO(data),
                                         content_type="application/json"
                                         ).get_environ())

        response = self.application(request)

        self.assertTrue(isinstance(response, Response))
        # WSGI responses are iterables. First element is the text.
        self.assertTrue(isinstance(response.response[0], basestring))

        self.assertTrue(response.response[0] == data)

    def test_handles_xml(self):

        # Note: Formatting the xml in this test causes failure.
        # Fairly certain this has to do with StringIO which uses newlines
        # as a delimeter.
        data = '<?xml version="1.0" ?><resource><test>1234</test></resource>'
        request = Request(EnvironBuilder(path='/',
                                         method='PUT',
                                         input_stream=StringIO(data),
                                         content_type="application/xml"
                                         ).get_environ())

        response = self.application(request)

        self.assertTrue(isinstance(response, Response))
        # WSGI responses are iterables. First element is the text.
        self.assertTrue(isinstance(response.response[0], basestring))

        # Remove all the formatting from the response before comparison.
        self.assertTrue((response.
                         response[0].
                         replace('\n', '').
                         replace('\t', '')) == data)
