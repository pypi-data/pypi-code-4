from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Response
from werkzeug.routing import Map, Rule

import unittest

from restpy.applications import RestApplication
from restpy.wsgi import UniqueEnvironMiddleware
from restpy.hooks import unique_request
from restpy.hooks import deserialize_request
from restpy.hooks import serialize_response


class TestUniqueRequestHook(unittest.TestCase):

    def setUp(self, *args, **kwargs):

        class TestEndpoint(object):

            def GET(endpoint_self, request):

                self.assertTrue(hasattr(request, 'uuid'))
                return Response("TEST")

            def PUT(endpoint_self, request):

                self.assertEqual(request.uuid, request.environ['uuid'])

                return Response("TEST")

        test_ulrs = Map([
            Rule('/', endpoint=TestEndpoint)
        ])

        super(TestUniqueRequestHook, self).setUp(*args, **kwargs)
        self.application = RestApplication(test_ulrs,
                                           pre_hooks=[unique_request])
        self.unique_application = UniqueEnvironMiddleware(self.application)

    def test_creates_uuid(self):

        environ = EnvironBuilder(path='/', method='GET').get_environ()

        self.application(environ, lambda: None)

    def test_detects_uuid(self):

        environ = EnvironBuilder(path='/', method='PUT').get_environ()

        self.unique_application(environ, lambda: None)


class TestDeserializeRequestHook(unittest.TestCase):

    def setUp(self, *args, **kwargs):

        class TestEndpoint(object):

            def GET(endpoint_self, request):

                self.assertTrue(hasattr(request, 'content'))
                self.assertTrue(isinstance(request.content, dict))
                self.assertTrue('test' in request.content)
                self.assertTrue(request.content['test'])
                return Response("TEST")

        test_ulrs = Map([
            Rule('/', endpoint=TestEndpoint)
        ])

        super(TestDeserializeRequestHook, self).setUp(*args, **kwargs)
        self.application = RestApplication(test_ulrs,
                                           pre_hooks=[deserialize_request])

    def test_deserializes_json(self):

        environ = EnvironBuilder(path='/',
                                 method='GET',
                                 content_type='application/json',
                                 data='{"test": true}').get_environ()

        self.application(environ, lambda: None)

    def test_deserializes_xml(self):

        environ = EnvironBuilder(path='/',
                                 method='GET',
                                 content_type='application/xml',
                                 data='<resource><test>True</test></resource>'
                                 ).get_environ()

        self.application(environ, lambda: None)


class TestSerializeResponseHook(unittest.TestCase):

    def setUp(self, *args, **kwargs):

        class TestEndpoint(object):

            def GET(endpoint_self, request):

                return Response({"test": True})

        test_ulrs = Map([
            Rule('/', endpoint=TestEndpoint)
        ])

        super(TestSerializeResponseHook, self).setUp(*args, **kwargs)
        self.application = RestApplication(test_ulrs,
                                           post_hooks=[serialize_response])

    def test_serializes_json(self):

        environ = EnvironBuilder(path='/',
                                 method='GET',
                                 headers={"accept": "application/json"}
                                 ).get_environ()

        response = self.application(environ, lambda: None)

        self.assertTrue(hasattr(response, 'data'))
        self.assertTrue(isinstance(response.data, basestring))
        self.assertEqual(response.data, '{"test": true}')

    def test_serializes_xml(self):

        environ = EnvironBuilder(path='/',
                                 method='GET',
                                 headers={"accept": "application/xml"}
                                 ).get_environ()

        response = self.application(environ, lambda: None)

        self.assertTrue(hasattr(response, 'data'))
        self.assertTrue(isinstance(response.data, basestring))
        self.assertEqual(response.data,
                         '<?xml version="1.0" ?>\n'
                         '<resource>\n'
                         '\t<test>True</test>\n'
                         '</resource>\n')
