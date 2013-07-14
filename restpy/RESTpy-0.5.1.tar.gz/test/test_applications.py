from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Response
from werkzeug.routing import Rule
from werkzeug.exceptions import MethodNotAllowed, NotFound, BadRequest

import pytest

from restpy.applications import RestApplication


@pytest.fixture
def urls():

    class TestEndpoint(object):

        def GET(self, request):

            return Response("TEST")

        def POST(self, request):

            raise BadRequest("TEST")

    test_ulrs = [
        Rule('/', endpoint=TestEndpoint)
    ]

    return test_ulrs


@pytest.fixture
def app(urls):

    return RestApplication(services=[{"urls": urls}],
                           request_hooks=[],
                           response_hooks=[])


def test_verb_routing_success(app):

    environ = EnvironBuilder(path='/', method='GET').get_environ()

    response = app(environ, lambda: None)

    assert response.status_code == 200
    assert response.data == "TEST"


def test_verb_routing_failure(app):

    environ = EnvironBuilder(path='/', method='PUT').get_environ()
    response = app(environ, lambda: None)

    assert isinstance(response, MethodNotAllowed)


def test_route_not_found(app):

    environ = EnvironBuilder(path='/notfound',
                             method='GET').get_environ()
    response = app(environ, lambda: None)

    assert isinstance(response, NotFound)


def test_application_raises_exception(app):

    environ = EnvironBuilder(path='/',
                             method='POST').get_environ()
    response = app(environ, lambda: None)

    assert isinstance(response, BadRequest)
