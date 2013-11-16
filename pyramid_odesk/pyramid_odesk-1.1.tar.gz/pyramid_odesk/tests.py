import unittest

from pyramid.testing import DummyRequest
from pyramid.httpexceptions import HTTPMethodNotAllowed


class AuthUnitTests(unittest.TestCase):

    HTTP_METHODS = ('GET', 'POST', 'PUT', 'DELETE')

    def test_base_handler(self):
        from .views import BaseHandler

        request = DummyRequest()

        for method in self.HTTP_METHODS:
            request.method = method
            instance = BaseHandler(request)
            self.assertRaises(HTTPMethodNotAllowed, instance.__call__)

    def test_base_handler_dispatch(self):
        from .views import BaseHandler

        request = DummyRequest()

        for method in self.HTTP_METHODS:
            request.method = method
            instance = BaseHandler(request)
            self.assertRaises(HTTPMethodNotAllowed, instance.__call__)
