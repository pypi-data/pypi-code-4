from flea import TestAgent
from nose.tools import assert_equal
from fresco import Response
from fresco import FrescoApp, GET, POST
from fresco import Route, routefor, urlfor, context
from .fixtures import CBV


class TestFrescoApp(object):

    def test_route_operates_as_a_decorator(self):

        app = FrescoApp()

        @app.route('/', GET)
        def view(req):
            return Response(['ok'])

        assert TestAgent(app).get('/').body == 'ok'

    def test_route_decorator_sets_url_property(self):
        app = FrescoApp()

        @app.route('/', GET)
        def view(req):
            return Response(['ok'])

        assert callable(view.url)

    def test_route_operates_as_a_function(self):

        def view(req):
            return Response(['ok'])

        app = FrescoApp()
        app.route('/', GET, view)
        assert TestAgent(app).get('/').body == 'ok'

    def test_route_returns_route_instance(self):
        def view(req):
            return Response(['ok'])

        app = FrescoApp()
        assert isinstance(app.route('/', GET, view), Route)

    def test_route_http_methods(self):

        def view(request):
            return Response([request.environ['REQUEST_METHOD']])

        app = FrescoApp()
        app.route('/get', GET, view)
        app.route('/post', POST, view)

        assert TestAgent(app).get('/get', check_status=False).response.status_code == 200
        assert TestAgent(app).post('/get', data={}, check_status=False).response.status_code == 405

        assert TestAgent(app).get('/post', check_status=False).response.status_code == 405
        assert TestAgent(app).post('/post', data={}, check_status=False).response.status_code == 200

    def test_HEAD_request_delegated_to_GET_view(self):

        app = FrescoApp()

        @app.route('/', GET)
        def view(req):
            return Response(['ok'], x_original_view='GET')

        assert TestAgent(app).get('/').body == 'ok'
        assert TestAgent(app).get('/').response.get_header('X-Original-View') == 'GET'
        ta = TestAgent(app)
        assert ta._request(ta.make_environ('HEAD', '/',)).response.get_header('X-Original-View') == 'GET'

    def test_NotFound_observed_when_raised_in_handler(self):

        def app1(req):
            from fresco.exceptions import NotFound
            if 'foo' in req.path_info:
                raise NotFound()
            return Response(['app1'])

        def app2(req):
            return Response(['app2'])

        app = FrescoApp()
        app.route_all('/', GET, app1)
        app.route_all('/', GET, app2)
        assert_equal(TestAgent(app).get('/bar').body, 'app1')
        assert_equal(TestAgent(app).get('/foo').body, 'app2')

    def test_NotFoundFinal_observed_when_raised_in_handler(self):

        def app1(req):
            from fresco.exceptions import NotFoundFinal
            if 'foo' in req.path_info:
                raise NotFoundFinal()
            return Response(['app1'])

        def app2(req):
            return Response(['app2'])

        app = FrescoApp()
        app.route_all('/', GET, app1)
        app.route_all('/', GET, app2)
        assert_equal(TestAgent(app).get('/bar').body, 'app1')
        assert_equal(TestAgent(app).get('/foo/', check_status=False).response.status_code, 404)

    def test_apps_called_in_correct_order(self):

        def view(req, value=''):
            return Response([value])

        app = FrescoApp()
        app.route_all('/f', GET, view, value='foo')
        app.route_all('/', GET, view, value='bar')
        assert_equal(TestAgent(app).get('/f/bar').body, 'foo')
        assert_equal(TestAgent(app).get('/b/bar').body, 'bar')

    def test_wsgi_app_handles_response_exceptions(self):

        from fresco.exceptions import NotFound

        def view(req):
            raise NotFound()

        app = FrescoApp()
        app.route('/', GET, view)
        assert_equal(TestAgent(app).get('/', check_status=False).response.status_code, 404)

    def test_route_wsgi_app(self):

        def wsgiapp(environ, start_response):

            start_response('200 OK', [('Content-Type', 'application/x-pachyderm')])
            return ['pretty pink elephants']

        app = FrescoApp()
        app.route_wsgi('/', wsgiapp)
        r = TestAgent(app).get('/')
        assert_equal(r.body, 'pretty pink elephants')
        assert_equal(r.response.get_header('Content-Type'), 'application/x-pachyderm')

class TestIncludeApp(object):

    def test_include_app(self):

        app = FrescoApp()
        @app.route('/', GET)
        def view(req):
            return Response(['ok'])

        app2 = FrescoApp()
        app2.include('/app1', app)

        assert TestAgent(app2).get('/', check_status=False).response.status_code == 404
        assert TestAgent(app2).get('/app1/', check_status=False).body == 'ok'

    def test_include_app_url_methods(self):

        app = FrescoApp()
        @app.route('/', GET)
        def view(req):
            return Response(view.url())

        app2 = FrescoApp()
        app2.include('/app1', app)

        assert_equal(TestAgent(app2).get('/app1/').body, 'http://127.0.0.1:8080/app1/')

class TestTrailingSlashes(object):

    """\
    The general principle is that if a GET or HEAD request is received for a
    URL without a trailing slash and no match is found, the app will look for a
    URL with a trailing slash, and redirect the client if such a route exists.
    """

    def test_no_trailing_slash(self):

        def foo(request):
            return Response(['foo'])

        app = FrescoApp()
        app.route('/foo/', GET, foo)

        r = TestAgent(app).get('/foo', follow=False)
        assert_equal(r.response.get_header('location'), 'http://127.0.0.1:8080/foo/')
        assert_equal(r.response.status_code, 301)

class TestViewCollection(object):


    def test_appdef(self):

        app = FrescoApp()
        app.include('/', CBV('bananas!'))
        assert_equal(TestAgent(app).get('/').body, 'bananas!')

    def test_appdef_url_generation(self):

        foo = CBV('foo!')
        bar = CBV('bar!')
        baz = CBV('baz!')

        app = FrescoApp(foo)
        app.include('/bar', bar)
        app.include('/baz', baz)

        with app.requestcontext():
            assert_equal(urlfor(foo.index_html), 'http://localhost/')
            assert_equal(urlfor(bar.index_html), 'http://localhost/bar/')
            assert_equal(urlfor(baz.index_html), 'http://localhost/baz/')

    def test_instance_available_in_context(self):

        s = []
        class MyCBV(CBV):

            def index_html(self, request):
                from fresco import context
                s.append(context.view_self)
                return Response([])

        instance = MyCBV('foo!')
        app = FrescoApp(instance)

        TestAgent(app).get('/')

        assert s[0] is instance


class TestURLGeneration(object):

    def test_urlfor_with_view_function(self):

        app = FrescoApp()
        @app.route('/foo', GET)
        def view(req):
            return Response(['ok'])

        with app.requestcontext():
            assert_equal(urlfor(view), 'http://localhost/foo')

    def test_urlfor_allows_script_name(self):

        app = FrescoApp()
        @app.route('/foo', GET)
        def view(req):
            return Response(['ok'])

        with app.requestcontext():
            assert_equal(urlfor(view, _script_name='/abc'), 'http://localhost/abc/foo')

    def test_urlfor_with_string(self):
        global myviewfunc
        myviewfunc = lambda req: Response(['ok'])
        app = FrescoApp()
        app.route('/myviewfunc', GET, myviewfunc)
        with app.requestcontext():
            assert_equal(urlfor('fresco.tests.test_core:myviewfunc'), 'http://localhost/myviewfunc')

    def test_urlfor_drops_query(self):
        myviewfunc = lambda req: Response([])
        app = FrescoApp()
        app.route('/', GET, myviewfunc)
        with app.requestcontext():
            assert_equal(urlfor(myviewfunc), 'http://localhost/')

    def test_urlfor_generates_first_route(self):

        myviewfunc = lambda req: Response([])
        app = FrescoApp()
        app.route('/1', GET, myviewfunc)
        app.route('/2', GET, myviewfunc)
        with app.requestcontext():
            assert_equal(urlfor(myviewfunc), 'http://localhost/1')

    def test_urlfor_with_class_based_view_spec(self):

        app = FrescoApp()
        app.include('/foo', CBV('x'))
        with app.requestcontext():
            assert_equal(urlfor('fresco.tests.fixtures:CBV.index_html'),
                         'http://localhost/foo/')

    def test_urlfor_with_class_based_view_unbound_method(self):

        app = FrescoApp()
        app.include('/foo', CBV('x'))
        with app.requestcontext():
            assert_equal(urlfor(CBV.index_html), 'http://localhost/foo/')

    def test_routefor_with_view_function(self):

        def view(req):
            return Response(['ok'])

        app = FrescoApp()
        route = app.route('/foo', GET, view)

        with app.requestcontext():
            assert_equal(routefor(view), route)

    def test_routefor_with_string(self):
        global myviewfunc
        myviewfunc = lambda req: Response(['ok'])
        app = FrescoApp()
        route = app.route('/myviewfunc', GET, myviewfunc)
        with app.requestcontext():
            assert_equal(routefor('fresco.tests.test_core:myviewfunc'), route)

    def test_routefor_generates_first_route(self):

        myviewfunc = lambda req: Response([])
        app = FrescoApp()
        r1 = app.route('/1', GET, myviewfunc)
        app.route('/2', GET, myviewfunc)
        with app.requestcontext():
            assert_equal(routefor(myviewfunc), r1)


class TestContextAttributes(object):

    def test_app_is_set(self):

        def check_app(request, expected):
            assert context.app is expected
            return Response([])

        app1 = FrescoApp()
        app2 = FrescoApp()

        app1.route('/', GET, check_app, {'expected': app1})
        app2.route('/', GET, check_app, {'expected': app2})

        TestAgent(app1).get('/')
        TestAgent(app2).get('/')


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


class TestResponseExceptions(object):

    def test_exception_is_converted_to_response(self):

        from fresco.exceptions import RedirectTemporary

        def redirector(request):
            raise RedirectTemporary('/foo')

        app = FrescoApp()
        app.route('/', GET, redirector)

        r = TestAgent(app).get('/', follow=False)
        assert r.response.status_code == 302

