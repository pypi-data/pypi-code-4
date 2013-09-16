from mock import Mock
from nose.tools import assert_equal
from fresco import Response
from fresco import FrescoApp, GET, POST, PUT, DELETE
from fresco import Route, urlfor, context
from fresco.util.wsgi import ClosingIterator
from . import fixtures


class TestFrescoApp(object):

    def test_route_operates_as_a_decorator(self):

        app = FrescoApp()

        @app.route('/', GET)
        def view():
            return Response(['ok'])

        with app.requestcontext('/'):
            assert app.view().content == ['ok']

    def test_route_decorator_sets_url_property(self):
        app = FrescoApp()

        @app.route('/', GET)
        def view():
            return Response(['ok'])

        assert callable(view.url)

    def test_route_operates_as_a_function(self):

        def view():
            return Response(['ok'])

        app = FrescoApp()
        app.route('/', GET, view)
        with app.requestcontext('/'):
            assert app.view().content == ['ok']

    def test_route_returns_route_instance(self):
        def view():
            return Response(['ok'])

        app = FrescoApp()
        assert isinstance(app.route('/', GET, view), Route)

    def test_route_http_methods(self):

        def view():
            return Response([context.request.environ['REQUEST_METHOD']])

        app = FrescoApp()
        app.route('/get', GET, view)
        app.route('/post', POST, view)

        with app.requestcontext('/get', REQUEST_METHOD='GET'):
            assert app.view().status_code == 200

        with app.requestcontext('/get', REQUEST_METHOD='POST'):
            assert app.view().status_code == 405

        with app.requestcontext('/post', REQUEST_METHOD='GET'):
            assert app.view().status_code == 405

        with app.requestcontext('/post', REQUEST_METHOD='POST'):
            assert app.view().status_code == 200

    def test_HEAD_request_delegated_to_GET_view(self):

        app = FrescoApp()

        @app.route('/', GET)
        def view():
            return Response([], x_original_view='GET')

        with app.requestcontext('/', REQUEST_METHOD='HEAD'):
            assert app.view().get_header('X-Original-View') == 'GET'

    def test_NotFound_observed_when_raised_in_handler(self):

        def app1():
            from fresco.exceptions import NotFound
            if 'foo' in context.request.path_info:
                raise NotFound()
            return Response(['app1'])

        def app2():
            return Response(['app2'])

        app = FrescoApp()
        app.route_all('/', GET, app1)
        app.route_all('/', GET, app2)

        with app.requestcontext('/bar'):
            assert app.view().content == ['app1']

        with app.requestcontext('/foo'):
            assert app.view().content == ['app2']

    def test_NotFound_final_observed_when_raised_in_handler(self):

        def app1():
            from fresco.exceptions import NotFound
            if 'foo' in context.request.path_info:
                raise NotFound(final=True)
            return Response(['app1'])

        def app2():
            return Response(['app2'])

        app = FrescoApp()
        app.route_all('/', GET, app1)
        app.route_all('/', GET, app2)

        with app.requestcontext('/bar'):
            assert app.view().content == ['app1']

        with app.requestcontext('/foo/'):
            assert app.view().status_code == 404

    def test_apps_called_in_correct_order(self):

        def view(value=''):
            return Response([value])

        app = FrescoApp()
        app.route_all('/f', GET, view, value='foo')
        app.route_all('/', GET, view, value='bar')

        with app.requestcontext('/f/bar'):
            assert app.view().content == ['foo']

        with app.requestcontext('/b/bar'):
            assert app.view().content == ['bar']

    def test_wsgi_app_handles_response_exceptions(self):

        from fresco.exceptions import NotFound

        def view():
            raise NotFound()

        app = FrescoApp()
        app.route('/', GET, view)

        with app.requestcontext('/'):
            assert app.view().status_code == 404

    def test_route_wsgi_app(self):

        def wsgiapp(environ, start_response):

            start_response('200 OK',
                           [('Content-Type', 'application/x-pachyderm')])
            return ['pretty pink elephants']

        app = FrescoApp()
        app.route_wsgi('/', wsgiapp)

        with app.requestcontext('/'):
            assert app.view().content == ['pretty pink elephants']
            assert app.view().get_header('Content-Type') == \
                    'application/x-pachyderm'

    def test_get_methods_matches_on_path(self):

        app = FrescoApp()
        app.route('/1', POST, lambda: None)
        app.route('/1', PUT, lambda: None)
        app.route('/2', GET, lambda: None)
        app.route('/2', DELETE, lambda: None)

        with app.requestcontext() as c:
            assert app.get_methods(app, c.request, '/1') == set([POST, PUT])

        with app.requestcontext() as c:
            assert app.get_methods(app, c.request, '/2') == set([GET, DELETE])

    def test_get_methods_matches_on_predicate(self):

        p1 = Mock(return_value=True)
        p2 = Mock(return_value=False)

        app = FrescoApp()
        app.route('/', POST, lambda: None, predicate=p1)
        app.route('/', PUT, lambda: None, predicate=p2)

        with app.requestcontext('/') as c:
            assert app.get_methods(app, c.request, '/') == set([POST])
            p1.assert_called_with(c.request)
            p2.assert_called_with(c.request)


class TestIncludeApp(object):

    def test_it_routes_to_an_included_app(self):

        app = FrescoApp()

        @app.route('/', GET)
        def view():
            return Response(['ok'])

        app2 = FrescoApp()
        app2.include('/app1', app)

        with app2.requestcontext('/'):
            assert app2.view().status_code == 404

        with app2.requestcontext('/app1/'):
            assert app2.view().content == ['ok']

    def test_included_app_can_use_urlfor(self):

        def view():
            url = urlfor(view)
            return Response(url)

        app = FrescoApp()
        app.route('/', GET, view)
        app2 = FrescoApp()
        app2.include('/app1', app)

        with app2.requestcontext('/app1/'):
            assert app2.view().content == 'http://localhost/app1/'


class TestTrailingSlashes(object):
    """\
    The general principle is that if a GET or HEAD request is received for a
    URL without a trailing slash and no match is found, the app will look for a
    URL with a trailing slash, and redirect the client if such a route exists.
    """

    def test_no_trailing_slash(self):

        def foo():
            return Response(['foo'])

        app = FrescoApp()
        app.route('/foo/', GET, foo)

        with app.requestcontext('/foo'):
            assert app.view().status_code == 301
            assert app.view().get_header('location') == 'http://localhost/foo/'


class TestViewCollection(object):

    def test_appdef(self):

        app = FrescoApp()
        app.include('/', fixtures.CBV('bananas!'))
        with app.requestcontext('/'):
            assert app.view().content == ['bananas!']

    def test_appdef_url_generation(self):

        foo = fixtures.CBV('foo!')
        bar = fixtures.CBV('bar!')
        baz = fixtures.CBV('baz!')

        app = FrescoApp(foo)
        app.include('/bar', bar)
        app.include('/baz', baz)

        with app.requestcontext():
            assert_equal(urlfor(foo.index_html), 'http://localhost/')
            assert_equal(urlfor(bar.index_html), 'http://localhost/bar/')
            assert_equal(urlfor(baz.index_html), 'http://localhost/baz/')

    def test_instance_available_in_context(self):

        s = []

        class MyCBV(fixtures.CBV):

            def index_html(self):
                from fresco import context
                s.append(context.view_self)
                return Response([])

        instance = MyCBV('foo!')
        app = FrescoApp(instance)

        with app.requestcontext('/'):
            app.view()
            assert s[0] is instance


class TestContextAttributes(object):

    def test_app_is_set(self):

        def check_app(expected):
            assert context.app is expected
            return Response([])

        app1 = FrescoApp()
        app2 = FrescoApp()

        app1.route('/', GET, check_app, {'expected': app1})
        app2.route('/', GET, check_app, {'expected': app2})

        with app1.requestcontext('/'):
            app1.view()

        with app2.requestcontext('/'):
            app2.view()


class TestAppRequestContext(object):

    def test_creates_isolated_context(self):

        app = FrescoApp()
        with app.requestcontext():
            context.request = 'foo'

            with app.requestcontext():
                context.request = 'bar'
                assert context.request == 'bar'

            assert context.request == 'foo'

    def test_parses_full_url(self):

        with FrescoApp().requestcontext('https://arthur@example.org:123/?x=y'):
            assert context.request.environ['HTTPS'] == 'on'
            assert context.request.environ['REMOTE_USER'] == 'arthur'
            assert context.request.environ['HTTP_HOST'] == 'example.org:123'
            assert context.request.environ['SCRIPT_NAME'] == ''
            assert context.request.environ['PATH_INFO'] == '/'
            assert context.request.environ['QUERY_STRING'] == 'x=y'

    def test_it_invokes_middleware(self):

        def middleware(app):
            def middleware(environ, start_response):
                environ['sausages'] = 1
                return app(environ, start_response)
            return middleware

        app = FrescoApp()
        app.add_middleware(middleware)
        with app.requestcontext() as c:
            assert 'sausages' in c.request.environ

    def test_it_closes_middleware(self):

        close = Mock()

        def middleware(app):
            def middleware(environ, start_response):
                return ClosingIterator(app(environ, start_response), close)
            return middleware

        app = FrescoApp()
        app.add_middleware(middleware)
        with app.requestcontext():
            pass
        assert close.call_count == 1

    def test_it_calls_first_iteration(self):
        """
        Some middleware waits until the first iteration to do things, so make
        sure we trigger this
        """
        from itertools import count
        counter = count()

        def middleware(app):
            def middleware(environ, start_response):
                iterator = app(environ, start_response)
                for item in iterator:
                    yield next(counter)
            return middleware

        app = FrescoApp()
        app.add_middleware(middleware)
        with app.requestcontext():
            assert next(counter) == 1


class TestResponseExceptions(object):

    def test_exception_is_converted_to_response(self):

        from fresco.exceptions import RedirectTemporary

        def redirector():
            raise RedirectTemporary('/foo')

        app = FrescoApp()
        app.route('/', GET, redirector)

        with app.requestcontext('/'):
            assert app.view().status_code == 302


class TestUrlfor(object):

    def test_urlfor_on_aliased_functions(self):

        view = lambda: None
        setattr(fixtures, 'aliased_view', view)

        app = FrescoApp()
        app.route('/', GET, view)
        with app.requestcontext():
            assert urlfor(view) == 'http://localhost/'
            assert urlfor('fresco.tests.fixtures.aliased_view') == \
                    'http://localhost/'

        delattr(fixtures, 'aliased_view')

    def test_urlfor_with_view_function(self):

        def view():
            return Response(['ok'])

        app = FrescoApp()
        app.route('/foo', GET, view)
        with app.requestcontext():
            assert urlfor(view) == 'http://localhost/foo'

    def test_urlfor_allows_script_name(self):

        def view():
            return Response(['ok'])

        app = FrescoApp()
        app.route('/foo', GET, view)
        with app.requestcontext():
            assert urlfor(view, _script_name='/abc') ==\
                    'http://localhost/abc/foo'

    def test_urlfor_with_string(self):
        app = FrescoApp()
        app.route('/myviewfunc', GET, fixtures.module_level_function)
        with app.requestcontext():
            assert urlfor('fresco.tests.fixtures.module_level_function') ==\
                    'http://localhost/myviewfunc'

    def test_urlfor_drops_query(self):
        myviewfunc = lambda req: Response([])
        app = FrescoApp()
        app.route('/', GET, myviewfunc)
        with app.requestcontext():
            assert urlfor(myviewfunc) == 'http://localhost/'

    def test_urlfor_generates_first_route(self):

        myviewfunc = lambda req: Response([])
        app = FrescoApp()
        app.route('/1', GET, myviewfunc)
        app.route('/2', GET, myviewfunc)
        with app.requestcontext():
            assert urlfor(myviewfunc) == 'http://localhost/1'

    def test_urlfor_with_class_based_view_spec(self):

        app = FrescoApp()
        app.include('/foo', fixtures.CBV('x'))
        with app.requestcontext():
            assert urlfor('fresco.tests.fixtures.CBV.index_html') ==\
                         'http://localhost/foo/'

    def test_it_uses_values_from_path_defaults(self):
        app = FrescoApp()
        app.route('/<test:int>', GET, lambda: None,
                  name='test', test_default=1)
        with app.requestcontext():
            assert urlfor('test') == 'http://localhost/1'

    def test_it_uses_callable_values_from_path_defaults(self):
        generate_value = Mock(return_value=1)
        app = FrescoApp()
        app.route('/<test:int>', GET, lambda: None,
                  name='test', test_default=generate_value)
        with app.requestcontext() as c:
            assert urlfor('test') == 'http://localhost/1'
            generate_value.assert_called_once_with(c.request)

    def test_path_defaults_removed_from_view_kwargs(self):
        app = FrescoApp()
        view = Mock()
        app.route('/<test:int>', GET, view,
                  name='test', test_default=1)
        with app.requestcontext('/2'):
            app.view()
            view.assert_called_with(test=2)
