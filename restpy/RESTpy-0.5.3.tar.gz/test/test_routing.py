from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Response
from werkzeug.routing import Rule
from werkzeug.exceptions import NotFound

import pytest
import uuid

from restpy.applications import RestApplication
from restpy.routing import UuidConverter


@pytest.fixture
def urls():

    class TestEndpoint(object):

        def GET(self, request, test):

            return Response("TEST")

    test_urls = [
        Rule('/<uuid:test>', endpoint=TestEndpoint)
    ]

    return test_urls


@pytest.fixture
def app(urls):

    return RestApplication(services=[{"urls": urls,
                                      "converters": {"uuid": UuidConverter}}],
                           request_hooks=[],
                           response_hooks=[])


def test_uuid_routing_success(app):

    environ = EnvironBuilder(path='/' + str(uuid.uuid4()),
                             method='GET').get_environ()

    response = app(environ, lambda: None)

    assert response.status_code == 200
    assert response.data == "TEST"


def test_uuid_routing_failure(app):

    environ = EnvironBuilder(path='/', method='POST').get_environ()
    response = app(environ, lambda: None)

    assert isinstance(response, NotFound)
