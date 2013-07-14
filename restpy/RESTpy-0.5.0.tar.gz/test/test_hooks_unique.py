from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Response
from werkzeug.routing import Rule

import pytest

from restpy.applications import RestApplication
from restpy.wsgi import UniqueEnvironMiddleware
from restpy.hooks import unique_request


@pytest.fixture
def urls():

    class TestEndpoint(object):

        def GET(endpoint_self, request):

            assert hasattr(request, 'uuid')
            return Response("TEST")

        def PUT(endpoint_self, request):

            assert request.uuid == request.environ['uuid']
            return Response("TEST")

    test_ulrs = [
        Rule('/', endpoint=TestEndpoint)
    ]

    return test_ulrs


@pytest.fixture
def app(urls):

    return RestApplication(services=[{"urls": urls}],
                           request_hooks=[unique_request],
                           response_hooks=[])


@pytest.fixture
def unique_app(app):
    return UniqueEnvironMiddleware(app)


def test_creates_uuid(app):

    environ = EnvironBuilder(path='/', method='GET').get_environ()

    app(environ, lambda: None)


def test_detects_uuid(unique_app):

    environ = EnvironBuilder(path='/', method='PUT').get_environ()

    unique_app(environ, lambda: None)
