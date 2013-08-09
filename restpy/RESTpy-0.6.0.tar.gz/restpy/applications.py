"""This defines a basic wsgi application that provides RESTful routing."""

from itertools import chain

from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import MethodNotAllowed
from werkzeug.exceptions import InternalServerError
from werkzeug.routing import Map
from werkzeug.wrappers import BaseRequest
from werkzeug.wrappers import BaseResponse
from werkzeug.wrappers import Request


class RestApplication(object):
    """Base REST application."""

    def __init__(self, services, request_hooks=None, response_hooks=None):

        self.services = services or []

        # If the first argument is already a werkzeug `Map` then use it.
        if isinstance(services, Map):

            self.url_map = services

        # Other wise, build a map from an iterable of `Rule` objects.
        else:

            # Build a list of url endpoints from the service interfaces.
            url_map = []
            converters = {}
            for service in services:
                url_map += (service.urls
                            if hasattr(service, 'urls')
                            else service['urls'])

                # Check for custom converters used by an application.
                custom_converters = {}
                if hasattr(service, 'converters'):
                    custom_converters = service.converters
                elif isinstance(service, dict) and 'converters' in service:
                    custom_converters = service['converters']

                converters = dict(chain(converters.iteritems(),
                                        custom_converters.iteritems()))

            self.url_map = Map(url_map, converters=converters)

        self.request_hooks = request_hooks or []
        self.response_hooks = response_hooks or []

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
        try:

            request = self.process_request_hooks(request)

        except HTTPException as e:

            response = e

            response = self.process_response_hooks(request, response)

            return response

        except Exception as e:

            response = InternalServerError(description=unicode(e))

            response = self.process_response_hooks(request, response)

            return response

        # The endpoint in this case is an object constructor which is why the
        # variable is captialzied.
        # This call automatically raises a `NotFound` exception if there is no
        # match found.

        try:

            Endpoint, kwargs = urls.match()

        except HTTPException as e:

            response = e

            response = self.process_response_hooks(request, response)

            return response

        handler_endpoint = Endpoint()

        try:

            handler_method = getattr(handler_endpoint, verb)

        except AttributeError:

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

            response = self.process_response_hooks(request, response)

            return response

        try:

            response = handler_method(request, **kwargs)

        except HTTPException as e:

            response = e

        except Exception as e:

            response = InternalServerError(description=unicode(e))

        response = self.process_response_hooks(request, response)

        return response

    def process_request_hooks(self, request):

        for hook in self.request_hooks:

            result = hook(request)

            if isinstance(result, BaseRequest):

                request = result

        return request

    def process_response_hooks(self, request, response):

        for hook in self.response_hooks:

            result = hook(request, response)

            if isinstance(result, BaseResponse):

                response = result

        return response
