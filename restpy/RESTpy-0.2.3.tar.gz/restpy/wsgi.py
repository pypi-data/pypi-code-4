"""This module contains wsgi middlewares.

All middlewares in this module are dependent on the `RequestMiddleware` which
is also included in this module.
"""

from werkzeug.exceptions import HTTPException, InternalServerError, BadRequest

from wrappers import Request

from utilities import xml_dump, xml_load
import json

from itertools import chain

import logging
logger = logging.getLogger(__name__)


class RequestMiddleware(object):
    """This middleware converts wsgi requests into request objects.

    This middleware should be the outer-most middleware anytime it is used
    to allow all inner middlewares and applications to simply accept a
    `request` object rather than a raw wsgi environ and to return a `response`
    object rather than directly dealing with `start_request` and iterators.
    """

    def __init__(self, application):

        self.application = application

    @Request.application
    def __call__(self, request):

        logger.info("Begin request %s.", request.uuid)
        response = self.application(request)
        logger.info("End request %s.", request.uuid)

        return response


class ExceptionHandlerMiddleware(object):
    """Wraps all request in exception handeling.

    The purpose of this wrapper is to allow all methods to `raise` exceptions
    rather than return them if desired.

    This wrapper also captures all unexpected exceptions and converts them
    into `InternalServerError` exceptions.
    """

    def __init__(self, application):

        self.application = application

    def __call__(self, request):

        try:
            return self.application(request)
        except HTTPException as e:
            return e
        except Exception as e:
            logging.error("An uncaught application error was detected during "
                          "request %s with message: %s.", request.uuid, str(e))
            return InternalServerError(description=unicode(e))


class SerializationMiddleware(object):
    """This middleware provides data serialization and deserialization.

    This module leverages the `Content-Type` and `Accept` headers to convert
    JSON or XML data into python dictionary for requests and python
    dictionaries to JSON or XML for responses.

    The values of all POST/PUT data and URL parameters are merged into a
    single python dictionary attached to the request under the `content`
    attribute.

    This middleware expects the return result from wrapped applications to be
    a response object containing either a dictionary or a list. All values
    contained in the response must be dictionaries, lists, or python primitive
    types to serialize.

    XML handeling is performed by functions in the `utilities` module.
    """

    def __init__(self, application):

        self.application = application

    def __call__(self, request):

        request.content = {}

        if request.data:
            try:
                logger.info("Begin deserialization for request %s.",
                            request.uuid)
                request = self._deserialize_request(request)
                logger.info("End deserialization for request %s.",
                            request.uuid)
            except:
                logger.info("Request %s contained invalid data.", request.uuid)
                return self._serialize_response(request,
                                                BadRequest("Data could not be "
                                                           "deserialized.")
                                                )

        response = self.application(request)

        logger.info("Begin serialization response for request %s.",
                    request.uuid)
        serialized_response = self._serialize_response(request, response)
        logger.info("End serialization response for request %s.", request.uuid)

        return serialized_response

    def _deserialize_request(self, request):

        if request.headers.get('content-type') == 'application/json':
            request.content = json.loads(request.data)

        elif request.headers.get('content-type') == 'application/xml':
            request.content = xml_load(request.data)

        else:
            request.content = request.data

        request.content = dict(chain(request.content.items(),
                                     request.args.items()
                                     )
                               )

        return request

    def _serialize_response(self, request, response):

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

        elif request.headers.get('content-type') == 'application/json':

            response.content_type = 'application/json'
            response.set_data(json.dumps(response.response))

        elif request.headers.get('content-type') == 'application/xml':

            response.content_type = 'application/xml'
            response.set_data(xml_dump(response.response))

        else:

            response.content_type = 'text/plain'
            response.set_data(unicode(response.response))

        return response
