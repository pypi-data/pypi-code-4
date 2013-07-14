from werkzeug.exceptions import HTTPException, BadRequest

import json
import uuid

from itertools import chain

from utilities import xml_dump, xml_load


def unique_request(request):
    """Assignes a UUID to the request.

    This hook will first look in the environ for a UUID. If found, it will
    assign that UUID to the request object. If not found it will create a
    new UUID for the request.
    """

    request.uuid = request.environ.get('uuid', str(uuid.uuid4()))


def deserialize_request(request):
    """A pre-hook that deserializes request data into Python data types."""

    try:
        if request.headers.get('content-type').upper() == 'APPLICATION/JSON':
            request.content = json.loads(request.data)

        elif request.headers.get('content-type').upper() == 'APPLICATION/XML':
            request.content = xml_load(request.data)

        else:
            request.content = {"POST": request.data}

        request.content = dict(chain(request.content.items(),
                                     request.args.items()
                                     )
                               )

        return request

    except:
        raise BadRequest()


def serialize_response(request, response):
    """A post-hook at serializes the response data into the requested MIME."""

    if isinstance(response, HTTPException):
        original_exception = response
        response = original_exception.get_response(request.environ)
        response.response = {
            "code": original_exception.code,
            "description": original_exception.description
        }

    if request.accept_mimetypes.accept_json:
        response.content_type = 'application/json'
        response.set_data(json.dumps(response.response))

    elif request.accept_mimetypes.accept_xhtml:
        response.content_type = 'application/xml'
        response.set_data(xml_dump(response.response))

    elif request.headers.get('content-type').upper() == 'APPLICATION/JSON':

        response.content_type = 'application/json'
        response.set_data(json.dumps(response.response))

    elif request.headers.get('content-type').upper() == 'APPLICATION/XML':

        response.content_type = 'application/xml'
        response.set_data(xml_dump(response.response))

    else:

        response.content_type = 'text/plain'
        response.set_data(unicode(response.response))

    return response
