from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Response, Request
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import MethodNotAllowed, NotFound

import unittest

from restpy.applications import RestApplication


class TestEndpoint(object):

    def GET(self, request):

        return Response("TEST")


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

        try:
            environ = EnvironBuilder(path='/', method='POST').get_environ()
            self.application(environ, lambda: None)
        except MethodNotAllowed:
            return

    def test_route_not_found(self):

        try:
            environ = EnvironBuilder(path='/notfound',
                                     method='GET').get_environ()
            self.application(environ, lambda: None)
        except NotFound:
            return
