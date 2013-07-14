from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Response
from werkzeug.routing import Rule
from werkzeug.exceptions import BadRequest

import pytest

from restpy.applications import RestApplication
from restpy.wsgi import ResponderMiddleware


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
def responder_app(app):

    return ResponderMiddleware(app)


def test_resolves_wsgi_application(responder_app):

    ran_start_response = {"test": False}

    def start_response(*args, **kwargs):

        ran_start_response["test"] = True

    environ = EnvironBuilder(path='/', method='GET').get_environ()

    response = responder_app(environ, start_response)

    iter(response)

    assert ran_start_response["test"] is True
