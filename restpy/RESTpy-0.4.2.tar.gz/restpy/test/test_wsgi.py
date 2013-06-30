from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import MethodNotAllowed, BadRequest

import unittest

from restpy.applications import RestApplication
from restpy.wsgi import UniqueEnvironMiddleware
from restpy.wsgi import ResponderMiddleware


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


class TestUniqueEnvironMiddleware(unittest.TestCase):

    def setUp(self, *args, **kwargs):

        super(TestUniqueEnvironMiddleware, self).setUp(*args, **kwargs)
        self.application = RestApplication(test_ulrs)
        self.application = UniqueEnvironMiddleware(self.application)

    def test_creates_uuid(self):

        environ = EnvironBuilder(path='/', method='GET').get_environ()

        self.application(environ, lambda: None)

        self.assertTrue('uuid' in environ)

    def test_creates_unique_uuid(self):

        environ_one = EnvironBuilder(path='/', method='GET').get_environ()

        self.application(environ_one, lambda: None)

        environ_two = EnvironBuilder(path='/', method='GET').get_environ()

        self.application(environ_two, lambda: None)

        self.assertNotEqual(environ_one['uuid'], environ_two['uuid'])


class TestResponderMiddleware(unittest.TestCase):

    def setUp(self, *args, **kwargs):

        super(TestResponderMiddleware, self).setUp(*args, **kwargs)
        self.application = RestApplication(test_ulrs)
        self.application = ResponderMiddleware(self.application)

    def test_resolves_wsgi_application(self):

        ran_start_response = {"test": False}

        def start_response(*args, **kwargs):

            ran_start_response["test"] = True

        environ = EnvironBuilder(path='/', method='GET').get_environ()

        response = self.application(environ, start_response)

        iter(response)
