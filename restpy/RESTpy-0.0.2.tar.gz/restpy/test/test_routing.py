from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Response, Request
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import MethodNotAllowed, NotFound

import unittest
import uuid

from restpy.applications import RestApplication
from restpy.routing import UuidConverter


class TestEndpoint(object):

    def GET(self, request, test):

        return Response("TEST")


test_ulrs = Map([
    Rule('/<uuid:test>', endpoint=TestEndpoint)
], converters={'uuid': UuidConverter})


class TestRouting(unittest.TestCase):

    def setUp(self, *args, **kwargs):

        super(TestRouting, self).setUp(*args, **kwargs)
        self.application = RestApplication(test_ulrs)

    def test_uuid_routing_success(self):

        request = Request(EnvironBuilder(path='/' + str(uuid.uuid4()),
                                         method='GET').get_environ())

        response = self.application(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, "TEST")

    def test_uuid_routing_failure(self):

        try:
            request = Request(EnvironBuilder(path='/',
                                             method='POST').get_environ())
            self.application(request)
        except NotFound:
            return
