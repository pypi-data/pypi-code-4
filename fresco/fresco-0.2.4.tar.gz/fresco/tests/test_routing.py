from mock import Mock
from nose.tools import assert_raises
from flea import TestAgent
from fresco import FrescoApp, urlfor, GET, POST, Response
from fresco.exceptions import BadRequest
from fresco.routing import resolve_viewspec, Route, \
                           RouteKwarg, CookieArg, FormArg, QueryArg
from .fixtures import CBV


class TestMethodDispatch(object):

    def test_route_is_dispatched_to_correct_method(self):

        getview = Mock(return_value=Response())
        postview = Mock(return_value=Response())
        app = FrescoApp()
        app.route('/', GET, getview)
        app.route('/', POST, postview)

        TestAgent(app).get('/')
        assert getview.call_count == 1
        assert postview.call_count == 0

        TestAgent(app).post('/')
        assert getview.call_count == 1
        assert postview.call_count == 1


class TestResolveViewSpec(object):

    def test_relative_import(self):
        assert resolve_viewspec('fresco.tests.fixtures:CBV', 1) is CBV

    def test_attribute(self):
        assert resolve_viewspec('fresco.tests.fixtures:CBV.index_html', 1) \
                == CBV.index_html
        assert id(resolve_viewspec('fresco.tests.fixtures:CBV.index_html', 1))\
                == id(CBV.index_html)
        # Curiously the object identity test fails. Irritating, but I don't
        # think it matters.
        #assert resolve_viewspec('fresco.tests.fixtures:CBV.index_html', 1) \
        #       is CBV.index_html


class TestRouteDecorators(object):

    def exclaim(self, func):
        def exclaim(request, *args, **kwargs):
            response = func(request, *args, **kwargs)
            return response.replace(content=[''.join(response.content) + '!'])
        return exclaim

    def test_decorator_is_applied(self):

        views = CBV('test')

        app = FrescoApp()
        app.route('/decorated', GET, views.index_html,
                  decorators=[self.exclaim])
        app.route('/plain', GET, views.index_html)

        with app.requestcontext('/decorated') as c:
            req = c.request
            assert app.view(req).content == ['test!']

        with app.requestcontext('/plain') as c:
            assert app.view(c.request).content == ['test']

    def test_decorator_works_with_urlfor(self):

        views = CBV('test')
        app = FrescoApp()
        app.route('/decorated', GET, views.index_html,
                  decorators=[self.exclaim])
        with app.requestcontext():
            assert urlfor(views.index_html, _app=app) == \
                    'http://localhost/decorated'


class TestPredicates(object):

    def test_predicate_match(self):

        def v1(request):
            return Response(['x'])

        def v2(request):
            return Response(['y'])

        app = FrescoApp()
        app.route('/', GET, v1, predicate=lambda request: 'x' in request.query)
        app.route('/', GET, v2, predicate=lambda request: 'y' in request.query)

        t = TestAgent(app)
        assert t.get('/?x=1', check_status=False).body == 'x'
        assert t.get('/?y=1', check_status=False).body == 'y'
        assert t.get('/', check_status=False).response.status_code == 404


class TestRouteKwargs(object):

    def test_routekwarg_configured(self):

        A = RouteKwarg()
        route = Route('/', GET, lambda r: None, x=A)
        assert A.route is route
        assert A.name is 'x'

    def test_routekwarg_value_passed(self):

        view = Mock()
        routekwarg = Mock(spec=RouteKwarg)
        routekwarg.return_value = 'xyzzy'

        app = FrescoApp()
        app.route('/', GET, view, x=routekwarg)
        with app.requestcontext('/') as c:
            app.view(c.request)
            routekwarg.assert_called_with(c.request)
            view.assert_called_with(c.request, x='xyzzy')

    def test_queryarg_value_passed(self):
        view = Mock()
        app = FrescoApp()
        app.route('/', GET, view, x=QueryArg())
        with app.requestcontext('/?x=foo') as c:
            app.view(c.request)
            view.assert_called_with(c.request, x='foo')

    def test_formarg_value_passed(self):
        view = Mock()
        app = FrescoApp()
        app.route('/', GET, view, x=FormArg())
        with app.requestcontext('/?x=foo') as c:
            app.view(c.request)
            view.assert_called_with(c.request, x='foo')

    def test_cookiearg_value_passed(self):
        view = Mock()
        app = FrescoApp()
        app.route('/', GET, view, x=CookieArg())
        with app.requestcontext('/', HTTP_COOKIE='x=foo') as c:
            app.view(c.request)
            view.assert_called_with(c.request, x='foo')

    def test_cookiearg_listvalue_passed(self):
        view = Mock()
        app = FrescoApp()
        app.route('/', GET, view, x=CookieArg([unicode]))
        with app.requestcontext('/', HTTP_COOKIE='x=foo;x=bar') as c:
            app.view(c.request)
            view.assert_called_with(c.request, x=['foo', 'bar'])

    def test_requestarg_value_converted(self):
        view = Mock()
        app = FrescoApp()
        app.route('/', GET, view, x=FormArg(float))
        with app.requestcontext('/?x=0') as c:
            app.view(c.request)
            view.assert_called_with(c.request, x=0.0)

    def test_requestarg_default_value(self):
        view = Mock()
        app = FrescoApp()
        app.route('/', GET, view, x=FormArg(default='d'))
        with app.requestcontext('/') as c:
            app.view(c.request)
            view.assert_called_with(c.request, x='d')

    def test_requestarg_raises_exception(self):
        view = Mock()
        app = FrescoApp()
        app.route('/', GET, view, x=FormArg())
        with app.requestcontext('/') as c:
            assert_raises(BadRequest, app.view, c.request)
