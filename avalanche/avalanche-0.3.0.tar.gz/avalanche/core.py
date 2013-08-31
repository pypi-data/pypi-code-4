# -*- coding: utf-8 -*-
"""
A basic WSGI web framework using class-based Request Handlers.
Uses webob for Request/Response objects.

The Avalanche framework is built on top of this.

The framework is composed of 5 parts:

  * Request -> abstraction for a HTTP request
  * Response -> abstraction for a HTTP response
  * RequestHandler -> contains the "user" code, generates responses
  * Router -> maps URLs to RequestHandlers
  * WSGIApplication -> Interface to http-server
                    -> uses router to dispatch requests to handlers


This implementation is based on webapp2 with the following differences:
  * use webob Request/Response classes without any extra methods defined
  * no backward compatibility with webob<1.1, webapp(1) and python2.5
  * removed support string imports
  * support just class-based RequestHandler
  * RequestHandler & WSGIApplication, removed globals (no thread-local)
  * removed config and registry from WSGIApplication
  * many other other internal API and implementation changes


  orignal webapp2 license:
    :copyright: 2011 by tipfy.org.
    :license: Apache Sotware License, see LICENSE.webapp2 for details.

"""

import logging
import sys
import traceback
import urllib.parse as urlparse

from webob import Request, Response
import webob.exc

from .router import Router


class RequestHandler:
    """Base HTTP request handler - this should be subclassed

    Attributes: ``app``, ``request``, ``response`` are references.

    Subclasses should implement the handled HTTP methods (``get``, ``post``, ...).
    The handler methods take \*args, \*\*kwargs from its route values.

    Subclasses may overwrite the ``handle_exception`` method.

    The methods ``redirect``, ``uri_for`` and ``redirect_to`` are helpers
    to be used on handler methods.

    The wsgi application executes the handler using the ``dispatch`` method.
    This can also be subclassed to add to some extra stuff.
    """

    def __init__(self, app, request):
        """
            :param app:
               (WSGIApplication)
            :param request:
               (Request)
        """
        self.app = app
        self.request = request
        self._response = None

    @property
    def response(self):
        """A reference to response object

        Handler method can just use a self.response and write on it or
        return a new response object.
        So the response is dinamically created on first access
        """
        if not self._response:
            self._response = self.app.RESPONSE_CLASS()
        return self._response

    @staticmethod
    def _normalize_handler_method(method):
        """Transforms an HTTP method into a valid Python identifier.

        :param method:
            (string) HTTP method name
        :return:
            (string)
        """
        return method.lower().replace('-', '_')

    def _get_handler_methods(self):
        """Returns a list (str) of HTTP methods supported by a handler.
        """
        has = lambda met: hasattr(self, self._normalize_handler_method(met))
        return [m for m in self.app.ALLOWED_METHODS if has(m)]


    def dispatch(self, *args, **kwargs):
        """Execute the handler method (``get``, ``post``, ...)

        Sets the ``response`` attribute.

        :param args:
            list of arguments to be passed to handler method
        :param kwargs:
            dict of arguments to be passed to handler method
        """

        # check if there's a handler_method defined
        method_name = self._normalize_handler_method(self.request.method)
        method = getattr(self, method_name, None)
        if method is None:
            # 405 Method Not Allowed.
            # The response MUST include an Allow header containing a
            # list of valid methods for the requested resource.
            # http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.6
            valid = ', '.join(self._get_handler_methods())
            raise webob.exc.HTTPMethodNotAllowed(headers=[('Allow', valid)])

        try:
            got = method(*args, **kwargs)
        except Exception as exception:
            got = self.handle_exception(exception)

        # overwrite response if handler returned a response
        if got is not None:
            self._response = got


    def redirect(self, uri, permanent=False, code=None, body=None):
        """sets the response with HTTP redirect to the given relative URI.

        :param uri:
            A relative or absolute URI (e.g., ``'../flowers.html'``).
        :param permanent:
            If True, uses a 301 redirect instead of a 302 redirect.
        :param code:
            The redirect status code. Supported codes are 301, 302, 303, 305,
            and 307.  300 is not supported because it's not a real redirect
            and 304 because it's the answer for a request with defined
            ``If-Modified-Since`` headers.
        :param body:
            Response body, if any.
        """
        if uri.startswith(('.', '/')):
            uri = str(urlparse.urljoin(self.request.url, uri))

        if code is None:
            if permanent:
                code = 301
            else:
                code = 302

        assert code in (301, 302, 303, 305, 307), \
            'Invalid redirect status code.'

        self.response.status = code
        self.response.text = ''
        self.response.headers['Location'] = uri
        if body is not None:
            self.response.write(body)


    def uri_for(self, _name, **kwargs):
        """Shortcut to build a URI from app router

        see also :meth:`avalanche.router.Router.build`
        """
        return self.app.router.build(_name, **kwargs)


    def redirect_to(self, _name, _permanent=False, _code=None,
                    _body=None, **kwargs):
        """Convenience method mixing :meth:`redirect` and :meth:`uri_for`.

        The arguments are described in :func:`redirect` and :func:`uri_for`.
        """
        uri = self.uri_for(_name, **kwargs)
        return self.redirect(uri, permanent=_permanent, code=_code, body=_body)


    def handle_exception(self, exception):
        """Called if this handler throws an exception during execution.

        The default behavior is to re-raise the exception to be handled by
        :meth:`WSGIApplication._handle_exception`.

        :param exception:
            The exception that was thrown.
        """
        raise





class WSGIApplication:
    """A WSGI application"""

    #: Allowed request methods.
    ALLOWED_METHODS = frozenset(
        ('GET', 'POST', 'HEAD', 'OPTIONS', 'PUT', 'DELETE', 'TRACE'))
    #: Class used for the request object.
    REQUEST_CLASS = Request
    #: Class used for the response object.
    RESPONSE_CLASS = Response

    #: Tempita template used on exceptions, use `detail` to show traceback
    BODY_TEMPLATE_500 = """
${explanation}<br /><br />
<pre style="background:#F2F2F2; padding:10px; font-size:14px">${detail}</pre>
<a href="${debug_link}">${debug_text}</a><br />
${html_comment}
"""
    BODY_TEMPLATE_404 = """
${explanation}<br /><br />
<pre style="background:#F2F2F2; padding:10px; font-size:14px">${detail}</pre>
${html_comment}
"""


    def __init__(self, routes=(), debug=False, error_handlers=None):
        """Initializes the WSGI application.

        :param routes:
            A sequence of :class:`Route` instances
        :param debug:
            True to enable debug mode, False otherwise.
            If value is (string) 'pdb' enables post-mortem debug using PDB
            on your terminal (if running on localhost only).

        :param error_handlers:
            A dictionary mapping HTTP error codes (int) to RequestHandler's
        """
        self.debug = debug
        self.router = Router(*routes)
        self.error_handlers = error_handlers or {}


    def __call__(self, environ, start_response):
        """Called by WSGI server when a request comes in.

        :param environ:
            A WSGI environment.
        :param start_response:
            A callable accepting a status code, a list of headers and an
            optional exception context to start the response.
        :returns:
            An iterable with the response to return to the client.
        """
        request = self.REQUEST_CLASS(environ)

        try:
            if request.method not in self.ALLOWED_METHODS:
                raise webob.exc.HTTPNotImplemented() # 501

            match_result = self.router.match(request)
            if not match_result:
                 # 404
                routes_info = self._debug_404() if self.debug else None
                raise webob.exc.HTTPNotFound(
                    detail=routes_info,
                    body_template=self.BODY_TEMPLATE_404)
            handler = match_result.route.endpoint(self, request)
            handler.dispatch(**match_result.kwargs)
            return handler.response(environ, start_response)

        except Exception as exception_1:
            try:
                # Try to handle it with a custom error handler
                response = self._handle_exception(request, exception_1)
                return response(environ, start_response)

            except webob.exc.HTTPException as exception_2:
                # webob HTTP exceptions are valid response objects
                return exception_2(environ, start_response)

            except Exception as exception_2:
                # exception not handled or error on exception handler
                response = self._internal_error(request, exception_2)
                return response(environ, start_response)


    def _debug_404(self):
        """return string with info on all defined routes"""
        routes = []
        for route in self.router.routes:
            routes.append("%s \t %s" % (route.template, route.name))
        return "Available Routes:\n\n%s" % "\n".join(routes)


    def _handle_exception(self, request, exception):
        """Handles an exception occurred in :meth:`__call__`.

        Use exception handlers registered in :attr:`error_handlers`.

        If the exception is not an ``HTTPException``, the status code 500
        is used.

        If no error handler is found, the exception is re-raised.

        Based on idea from `Flask`_.

        :param request:
            A :class:`Request` instance.
        :param exception:
            The uncaught exception.
        :returns:
            handler.response
        """
        if isinstance(exception, webob.exc.HTTPException):
            code = exception.code
        else:
            code = 500

        handler_class = self.error_handlers.get(code)
        if handler_class:
            handler = handler_class(self, request)
            handler.response.status = code
            handler.get(exception)
            return handler.response
        else:
            # Re-raise it to be caught by the WSGI app.
            raise


    def internal_error(self, exception):
        """called when an iternal error occurs, logs the exception

        this should be sub-classed to perform some extra operations on 500
        typically used to send email to admin/developers
        """
        logging.exception(exception)


    def _internal_error(self, request, exception):
        """default for non-handled exceptions, and framework errors
        if on debug mode includes traceback on HTTP response
        """
        self.internal_error(exception)

        # exception template uses vars from environ
        detail = None
        request.environ['debug_link'] = ''
        request.environ['debug_text'] = ''

        if self.debug:
            # get exception traceback
            exc_info = sys.exc_info()
            detail_lines = traceback.format_exception(*exc_info)
            if hasattr(exception, '__obj_stack__'):
                detail_lines.append('\nObject context:\n')
                detail_lines += traceback.format_list(exception.__obj_stack__)
            detail = ''.join(detail_lines)

            # pdb post-mortem debug is enabled
            if self.debug == 'pdb': # pragma: no cover
                self._pdb_debug(request, exc_info)

        return webob.exc.HTTPInternalServerError(
            detail=detail,
            body_template=self.BODY_TEMPLATE_500)


    def _pdb_debug(self, request, exc_info): # pragma: no cover
        # re-raise exception
        if request.GET.get("__a_debug__"):
            try:
                # try to use Ipython if available
                from IPython.ipapi import make_session; make_session()
                from IPython.Debugger import Pdb as IPdb
                Pdb = IPdb
            except:
                from pdb import Pdb
            debugger = Pdb()
            # FIXME: GAE have redirected stdin/stdout but it doesnt
            # support readline, so ignore it for now...
            # debugger = Pdb(stdin=sys.__stdin__, stdout=sys.__stdout__)
            debugger.reset()
            debugger.interaction(None, exc_info[2])

        # add link to activate debuging from terminal
        url_parts = list(urlparse.urlsplit(request.url))
        if '__a_debug__' not in url_parts[3]:
            if url_parts[3]:
                url_parts[3] += '&'
            url_parts[3] += '__a_debug__=1'
        request.environ['debug_link'] = urlparse.urlunsplit(url_parts)
        request.environ['debug_text'] = 'debug on terminal'
