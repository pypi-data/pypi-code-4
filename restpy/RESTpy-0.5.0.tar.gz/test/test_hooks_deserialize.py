from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Response
from werkzeug.routing import Rule

import pytest

from restpy.applications import RestApplication
from restpy.hooks import deserialize_request


@pytest.fixture
def urls():

    class TestEndpoint(object):

        def GET(endpoint_self, request):

            assert hasattr(request, 'content')
            assert isinstance(request.content, dict)
            assert 'test' in request.content
            assert request.content['test']
            return Response("TEST")

    test_ulrs = [
        Rule('/', endpoint=TestEndpoint)
    ]

    return test_ulrs


@pytest.fixture
def app(urls):

    return RestApplication(services=[{"urls": urls}],
                           request_hooks=[deserialize_request],
                           response_hooks=[])


def test_deserializes_json(app):

    environ = EnvironBuilder(path='/',
                             method='GET',
                             content_type='application/json',
                             data='{"test": true}').get_environ()

    app(environ, lambda: None)


def test_deserializes_xml(app):

    environ = EnvironBuilder(path='/',
                             method='GET',
                             content_type='application/xml',
                             data='<resource><test>True</test></resource>'
                             ).get_environ()

    app(environ, lambda: None)
