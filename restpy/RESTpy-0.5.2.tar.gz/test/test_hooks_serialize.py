from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Response
from werkzeug.routing import Rule

import pytest

from restpy.applications import RestApplication
from restpy.hooks import serialize_response


@pytest.fixture
def urls():

    class TestEndpoint(object):

        def GET(endpoint_self, request):

            return Response({"test": True})

    test_ulrs = [
        Rule('/', endpoint=TestEndpoint)
    ]

    return test_ulrs


@pytest.fixture
def app(urls):

    return RestApplication(services=[{"urls": urls}],
                           request_hooks=[],
                           response_hooks=[serialize_response])


def test_serializes_json(app):

    environ = EnvironBuilder(path='/',
                             method='GET',
                             headers={"accept": "application/json"}
                             ).get_environ()

    response = app(environ, lambda: None)

    assert hasattr(response, 'data')
    assert isinstance(response.data, basestring)
    assert response.data == '{"test": true}'


def test_serializes_xml(app):

    environ = EnvironBuilder(path='/',
                             method='GET',
                             headers={"accept": "application/xml"}
                             ).get_environ()

    response = app(environ, lambda: None)

    assert hasattr(response, 'data')
    assert isinstance(response.data, basestring)
    assert (response.data ==
            '<?xml version="1.0" ?>\n'
            '<resource>\n'
            '\t<test>True</test>\n'
            '</resource>\n')
