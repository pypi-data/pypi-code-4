import sys

from collections import defaultdict
from contextlib import contextmanager
from functools import partial
from io import BytesIO
from urllib import unquote
from urlparse import urlparse
from types import MethodType

import blinker

from fresco import Request
from fresco.response import Response
from fresco.util.urls import normpath

from fresco.exceptions import ResponseException, NotFound
from fresco.requestcontext import RequestContext
from fresco.routing import ExtensiblePattern, MatchAllURLsPattern, \
                           Route, resolve_viewspec, RouteKwarg
from fresco.options import Options

HTTP_METHODS = GET, HEAD, POST, PUT, DELETE = \
               'GET', 'HEAD', 'POST', 'PUT', 'DELETE'

__all__ = HTTP_METHODS + ('FrescoApp', 'context', 'routefor', 'urlfor')

#: Context for the current request; allows apps to access the current request
#: context as a pseudo-global var
context = RequestContext()

#: Class to use to instantiate request objects
request_class = Request


class FrescoApp(object):
    """\
    Fresco application class.
    """

    #: The default class to use for URL pattern matching
    pattern_class = ExtensiblePattern

    #: A stdlib logger object, or None
    logger = None

    def __init__(self, views=None, path=None):

        super(FrescoApp, self).__init__()

        from fresco.middleware import FlashMiddleware, context_middleware

        #: List of URL routes
        self.__routes__ = []

        #: List mapping view functions to routes
        self.__routed_views__ = {}

        #: A list of (middleware, args, kwargs) tuples
        self._middleware = []

        #: Middleware layers applied after any middleware added through
        #: :meth:`add_middleware`.
        self.core_middleware = [FlashMiddleware,
                                partial(context_middleware, frescoapp=self)]

        #: The WSGI application. Replaced every time new middleware is added.
        self._wsgi_app = self._make_wsgi_app()

        #: An options dictionary, for arbitrary application variables or
        #: configuration
        self.options = Options()

        self.signal_ns = blinker.Namespace()

        #: Sent when a request matches a route, immediately before the view is
        #: invoked.
        #: Receivers will be passed: route, view, view_args, view_kwargs
        self.route_matched = self.signal_ns.signal('route_matched')

        #: Sent Sent after a view function is invoked, before the response
        #: object is output.
        #: Receivers will be passed: view, request and response
        self.view_finished = self.signal_ns.signal('view_finished')

        if views:
            if path is None:
                path = '/'
            self.include(path, views)

    def __call__(self, environ, start_response):
        """\
        Call the app as a WSGI application
        """
        return self._wsgi_app(environ, start_response)

    def __unicode__(self):
        """\
        Unicode representation of the application and its configured routes
        """
        s = u'<%s\n' % self.__class__.__name__
        for route in self.__routes__:
            s += u'    ' + unicode(route)
        s += '>'
        return  s

    def view(self, request):
        """\
        Implement the fresco view interface
        """
        context.app = self
        environ = request.environ
        environ['fresco.app'] = self
        method = environ['REQUEST_METHOD'].upper()
        path = unquote(environ.get('PATH_INFO', '').decode(request.charset,
                                                           'replace'))

        if not path:
            path = u'/'

        for view, route, args, kwargs in self.gettarget(request, path,
                                                        method):
            for k, v in kwargs.items():
                if isinstance(v, RouteKwarg):
                    v = v(request)
                kwargs[k] = v

            environ['wsgiorg.routing_args'] = (args, kwargs)
            if route:
                context.view_self = getattr(route.original_view, 'im_self',
                                            None)
            try:
                self.route_matched.send(self, route=route, view=view,
                                        request=request)
                response = view(request, *args, **kwargs)
                self.view_finished.send(self, view=view, response=response)
                return response
            except NotFound:
                continue
            except ResponseException as e:
                return e.response

        if path[-1] != '/':
            for _ in self.gettarget(request, path + '/', method):
                return Response.redirect_permanent(path + '/')

        return Response.not_found()

    def add_middleware(self, middleware, *args, **kwargs):
        """\
        Add a WSGI middleware layer
        """
        self._middleware.append((middleware, args, kwargs))
        self._wsgi_app = self._make_wsgi_app()

    def _raw_wsgi_app(self, environ, start_response):
        return self.view(request_class(environ))(environ, start_response)

    def _make_wsgi_app(self):
        app = self._raw_wsgi_app
        for middleware, args, kwargs in self._middleware:
            app = middleware(app, *args, **kwargs)
        for middleware in self.core_middleware:
            app = middleware(app)
        return app

    def _add_url_method(self, func, route):
        """\
        Add a method at ``func.url`` that returns a URL generated from
        ``pattern``s pathfor method.
        """
        if hasattr(func, 'url'):
            return
        try:
            func.url = partial(urlfor, func)
        except AttributeError:
            # Cannot set function attributes on bound or unbound methods.
            # See http://www.python.org/dev/peps/pep-0232/
            pass

    def _add_route(self, route):
        self.__routes__.append(route)
        routes = self.__routed_views__.setdefault(route.original_view, {})

        # Allow lookup by unbound method too
        if isinstance(route.original_view, MethodType):
            unbound_method = getattr(route.original_view.im_class,
                                    route.original_view.__name__)
            self.__routed_views__[unbound_method] = routes

        routes.setdefault(route.tag, route)

        if '__default__' not in routes:
            routes['__default__'] = route

        self._add_url_method(route.original_view, route)

    def route(self, pattern, methods, view=None, *args, **kwargs):
        """
        Match a URL pattern to a view function. Can be used as a function
        decorator, in which case the ``view`` parameter should not be passed.

        :param pattern: A string that can be compiled into a path pattern
        :param methods: A list of HTTP methods the view is bound to
        :param view:    The view function. If not specified a function
                        decorator will be returned.

        Other parameters are as for the :class:`Route` constructor.
        """

        # Catch the common error of not providing a valid method
        if not isinstance(methods, basestring):
            try:
                methods = iter(methods)
            except TypeError:
                raise TypeError("Method argument must be a string or iterable")

        if view is None:
            def route_decorator(func):
                self._add_route(Route(pattern, methods, func, *args, **kwargs))
                return func
            return route_decorator

        route = Route(pattern, methods, view, *args, **kwargs)
        self._add_route(route)
        return route

    def route_wsgi(self, path, wsgiapp, *args, **kwargs):

        def fresco_wsgi_view(request):
            fake_start_response = lambda status, headers, exc_info=None: None
            return Response.from_wsgi(wsgiapp,
                                      request.environ,
                                      fake_start_response)

        return self.route_all(path, HTTP_METHODS, fresco_wsgi_view,
                              *args, **kwargs)

    def route_all(self, path, *args, **kwargs):
        """\
        Expose a view for all URLs starting with ``path``.

        :param path: the path prefix at which the view will be routed
        """
        return self.route(MatchAllURLsPattern(path), *args, **kwargs)

    def include(self, path, views):
        """
        Include a view collection at the given path.

        The included view collection's url properties will be modified to
        generate the prefixed URLs.

        :param path:  Path at which to include the views
        :param views: Any collection of views (must expose a ``__routes___``
                      attribute)
        """
        routes = list(r.add_prefix(path) for r in views.__routes__)
        for r in routes:
            r.resolve_view(views)
            self._add_route(r)

    def gettarget(self, request, path, method):
        """
        Generate routes matching the request URI.

        For each function matched, yield a tuple of::

            (view, route, positional_args, keyword_args)

        Where positional and keyword arguments are parsed from the URL
        """
        path = normpath(path)
        valid_methods = set()

        is_head = (method == 'HEAD')
        head_views = []

        matching_routes = []
        found = False

        for route in self.__routes__:
            result = route.pattern.match(path)
            if result is None:
                continue

            if route and route.predicate and not route.predicate(request):
                continue

            view_args, view_kwargs = result
            if route.view_kwargs:
                view_kwargs = dict(route.view_kwargs, **view_kwargs)

            matching_routes.append((route, view_args, view_kwargs))

            if method not in route.methods:
                valid_methods.update(route.methods)
                if is_head and 'GET' in route.methods:
                    head_views.append((_make_head_view(route.view), route,
                                       view_args, view_kwargs))
                continue

            found = True
            if self.logger:
                self.logger.info("gettarget: %s %r => %r", request.method, path,
                                 route.original_view)

            yield route.view, route, view_args, view_kwargs

        if found or not valid_methods:
            return

        if head_views:
            for item in head_views:
                yield item
            return

        if valid_methods:
            yield self.view_method_not_found, None, (valid_methods,), {}
            return

    def view_method_not_found(self, request, valid_methods):
        """
        Return a ``405 Method Not Allowed`` response.

        Called when a view matched the pattern but no HTTP methods matched.
        """
        return Response.method_not_allowed(valid_methods)

    @contextmanager
    def requestcontext(self, url='http://localhost/', environ=None, **kwargs):
        """
        Return the global :class:`fresco.requestcontext.RequestContext`
        instance, populated with a new request object modelling default
        WSGI environ values.

        Synopsis::

            >>> app = FrescoApp()
            >>> with app.requestcontext('http://www.example.com/view') as c:
            ...     print c.request.url
            ...
            http://www.example.com/view

        """
        url = urlparse(url)
        netloc = url.netloc
        user = ''
        if '@' in netloc:
            user, netloc = netloc.split('@', 1)

        if ':' in user:
            user, _ = user.split(':')[0]

        env_overrides = environ or {}
        env_overrides.update(kwargs)

        environ = {
            'REQUEST_METHOD': 'GET',
            'SERVER_NAME': 'localhost',
            'SERVER_PORT': '80',
            'SERVER_PROTOCOL': 'HTTP/1.0',
            'HTTP_HOST': netloc or 'localhost',
            'SCRIPT_NAME': '',
            'PATH_INFO': url.path,
            'REMOTE_ADDR': '127.0.0.1',
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': url.scheme or 'http',
            'wsgi.input': BytesIO(),
            'wsgi.errors': sys.stderr,
            'wsgi.multithread': True,
            'wsgi.multiprocess': True,
            'wsgi.run_once': False,
        }
        if url.scheme == 'https':
            environ['HTTPS'] = 'on'
            environ['SERVER_PORT'] = '443'

        if user:
            environ['REMOTE_USER'] = user

        if url.query:
            environ['QUERY_STRING'] = url.query

        environ.update(env_overrides)
        context.push(request=request_class(environ), app=self)
        yield context
        context.pop()


def collect_keys(items):
    """
    [(k1, v1), (k1, v2), (k2, v3)] -> [(k1, [v1, v2]), (k2, [v3])]
    """
    d = defaultdict(list)
    for key, value in items:
        d[key].append(value)
    return d.items()


def _make_head_view(view):
    """\
    Take a view that responds to a ``GET`` request and adapt it to one that
    will handle ``HEAD`` requests.
    """

    def head_view(*args, **kwargs):
        return view(*args, **kwargs).replace(content=[], content_length=0)
    return head_view


def routefor(viewspec, tag='__default__', _app=None):
    """\
    Return the Route corresponding to the given view function

    :param viewspec: a view callable or a string in the form
                     'package.module:viewfunction'
    :param tag: The URL tag for retrieving a named URL.
    :param _app: The app object. If None, the current app will be used.
    """
    app = _app or context.app
    viewspec = resolve_viewspec(viewspec, stack_depth=2)
    return app.__routed_views__[viewspec][tag]


def urlfor(viewspec, _tag='__default__', **kwargs):
    """\
    Return the url for the given view function

    :param viewspec: a view callable or a string in the form
                     'package.module:viewfunction'
    :param _tag: The URL tag for retrieving a named URL.
    :param _app: The app object. If None, the current app will be used.
    :param _request: the current request object.
    :param _scheme: the URL scheme to use (eg 'https' or 'http').
    :param _netloc: the network location to use (eg 'localhost:8000').
    :param _script_name: the SCRIPT_NAME path component
    :param _query: any query parameters, as a dict or list of
                    ``(key, value)`` tuples.
    :param _fragment: a URL fragment to append.
    """
    app = kwargs.get('_app') or context.app
    viewspec = resolve_viewspec(viewspec, stack_depth=2)
    return app.__routed_views__[viewspec][_tag].url(**kwargs)
