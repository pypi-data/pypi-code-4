from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import MethodNotAllowed, NotFound, BadRequest

import unittest

from restpy.applications import RestApplication


class TestEndpoint(object):

    def GET(self, request):

        return Response("TEST")

    def POST(self, request):

        raise BadRequest("TEST")


test_ulrs = Map([
    Rule('/', endpoint=TestEndpoint)
])


class TestApplication(unittest.TestCase):

    def setUp(self, *args, **kwargs):

        super(TestApplication, self).setUp(*args, **kwargs)
        self.application = RestApplication(test_ulrs)

    def test_verb_routing_success(self):

        environ = EnvironBuilder(path='/', method='GET').get_environ()

        response = self.application(environ, lambda: None)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, "TEST")

    def test_verb_routing_failure(self):

        environ = EnvironBuilder(path='/', method='PUT').get_environ()
        response = self.application(environ, lambda: None)

        self.assertTrue(isinstance(response, MethodNotAllowed))

    def test_route_not_found(self):

        environ = EnvironBuilder(path='/notfound',
                                 method='GET').get_environ()
        response = self.application(environ, lambda: None)

        self.assertTrue(isinstance(response, NotFound))

    def test_application_raises_exception(self):

        environ = EnvironBuilder(path='/',
                                 method='POST').get_environ()
        response = self.application(environ, lambda: None)

        self.assertTrue(isinstance(response, BadRequest))
