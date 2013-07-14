from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Response
from werkzeug.routing import Rule
from werkzeug.exceptions import BadRequest

import pytest

from restpy.applications import RestApplication
from restpy.wsgi import UniqueEnvironMiddleware


@pytest.fixture
def urls():

    class TestEndpoint(object):

        def GET(self, request):

            return Response("TEST")

        def POST(self, request):

            raise BadRequest("TEST")

        def PUT(self, request):

            return Response(request.content)

    test_urls = [
        Rule('/', endpoint=TestEndpoint)
    ]

    return test_urls


@pytest.fixture
def app(urls):

    return RestApplication(services=[{"urls": urls}],
                           request_hooks=[],
                           response_hooks=[])


@pytest.fixture
def unique_app(app):

    return UniqueEnvironMiddleware(app)


def test_creates_uuid(unique_app):

    environ = EnvironBuilder(path='/', method='GET').get_environ()

    unique_app(environ, lambda: None)

    assert 'uuid' in environ


def test_creates_unique_uuid(unique_app):

    environ_one = EnvironBuilder(path='/', method='GET').get_environ()

    unique_app(environ_one, lambda: None)

    environ_two = EnvironBuilder(path='/', method='GET').get_environ()

    unique_app(environ_two, lambda: None)

    assert environ_one['uuid'] != environ_two['uuid']
