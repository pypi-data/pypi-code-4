"""This defines a basic wsgi application that provides RESTful routing."""

from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import MethodNotAllowed
from werkzeug.exceptions import InternalServerError
from werkzeug.wrappers import Request, BaseRequest, BaseResponse


class RestApplication(object):
    """Base REST application.

    This object uses a werkzeug url map to route a request to the appropriate
    endpoint. Once an enpoint is found it attempts to call a method with the
    same name as the requested verb. For example, a GET request will look for
    the GET method of the endpoint to call.

    All verbs are upper-cased.

    Note::

        This application requires that it be wrapped in the `RequestMiddleware`
        found in the `wsgi` module.
    """

    def __init__(self, url_map, pre_hooks=None, post_hooks=None):

        self.url_map = url_map
        self.pre_hooks = pre_hooks or []
        self.post_hooks = post_hooks or []

    def __call__(self, environ, start_response):

        request = Request(environ)

        # Werkzeug documentation shows, but does not promise, that request
        # methods are upper case already. Since it isn't explicitly promised
        # this line was added.
        verb = request.method.upper()

        # Standard werkzeug functionality to create a `MapAdapter` object that
        # can route requests.
        urls = self.url_map.bind_to_environ(request.environ)

        # Attempt to process pre-request hooks.
        print "PROCESSING REQUEST HOOKS"
        try:

            request = self.process_request_hooks(request)

        except HTTPException as e:

            print "REQUEST HOOK HTTP EXCEPTION"

            response = e

            response = self.process_response_hooks(request, response)

            return response

        except Exception as e:

            print "REQUEST HOOK PY EXCEPTION"

            response = InternalServerError(description=unicode(e))

            response = self.process_response_hooks(request, response)

            return response

        # The endpoint in this case is an object constructor which is why the
        # variable is captialzied.
        # This call automatically raises a `NotFound` exception if there is no
        # match found.
        print "MATCHING URLS"
        try:

            Endpoint, kwargs = urls.match()

        except HTTPException as e:

            print "URL HTTP EXCEPTION"

            response = e

            print "PROCESSING RESPONSE HOOKS"
            response = self.process_response_hooks(request, response)

            return response

        handler_endpoint = Endpoint()

        print "FINDING METHOD"
        try:

            handler_method = getattr(handler_endpoint, verb)

        except AttributeError:

            print "METHOD NOT FOUND"
            # If method not found then generate a list of allowed methods.
            # The list of allowed methods is required to satisfy the HTTP
            # standard for Method Now Allowed. Currently only matches GET,
            # POST, PUT, and DELETE when producing a list.
            response = MethodNotAllowed(valid_methods=[m for m
                                                       in dir(handler_endpoint)
                                                       if m
                                                       in ['GET',
                                                           'POST',
                                                           'PUT',
                                                           'DELETE'
                                                           ]
                                                       ])

            print "PROCESSING POST HOOKS"
            response = self.process_response_hooks(request, response)

            return response

        print "EXECUTING METHOD"
        try:

            response = handler_method(request, **kwargs)

        except HTTPException as e:

            print "EXECUTION WAS HTTP EXCEPTION"

            response = e

        except Exception as e:

            print "EXECUTION WAS PY EXCEPTION"

            response = InternalServerError(description=unicode(e))

        print "PROCESSING RESPONSE HOOKS"
        response = self.process_response_hooks(request, response)

        return response

    def process_request_hooks(self, request):

        for hook in self.pre_hooks:

            result = hook(request)

            if isinstance(result, BaseRequest):

                request = result

        return request

    def process_response_hooks(self, request, response):

        for hook in self.post_hooks:

            result = hook(request, response)

            if isinstance(result, BaseResponse):

                response = result

        return response
