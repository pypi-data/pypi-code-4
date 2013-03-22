from nose.tools import ok_, eq_, raises

from flask import Flask, request
from flask.views import MethodView
from flask.ext.admin import base


class MockView(base.BaseView):
    # Various properties
    allow_call = True
    allow_access = True

    @base.expose('/')
    def index(self):
        return 'Success!'

    @base.expose('/test/')
    def test(self):
        return self.render('mock.html')

    def _handle_view(self, name, **kwargs):
        if self.allow_call:
            return super(MockView, self)._handle_view(name, **kwargs)
        else:
            return 'Failure!'

    def is_accessible(self):
        if self.allow_access:
            return super(MockView, self).is_accessible()
        else:
            return False

class MockMethodView(base.BaseView):
    @base.expose('/')
    def index(self):
        return 'Success!'

    @base.expose_plugview('/_api/1')
    class API1(MethodView):
        def get(self, cls):
            return cls.render('method.html', request=request, name='API1')
        def post(self, cls):
            return cls.render('method.html', request=request, name='API1')
        def put(self, cls):
            return cls.render('method.html', request=request, name='API1')
        def delete(self, cls):
            return cls.render('method.html', request=request, name='API1')

    @base.expose_plugview('/_api/2')
    class API2(MethodView):
        def get(self, cls):
            return cls.render('method.html', request=request, name='API2')
        def post(self, cls):
            return cls.render('method.html', request=request, name='API2')

def test_baseview_defaults():
    view = MockView()
    eq_(view.name, None)
    eq_(view.category, None)
    eq_(view.endpoint, None)
    eq_(view.url, None)
    eq_(view.static_folder, None)
    eq_(view.admin, None)
    eq_(view.blueprint, None)


def test_base_defaults():
    admin = base.Admin()
    eq_(admin.name, 'Admin')
    eq_(admin.url, '/admin')
    eq_(admin.endpoint, 'admin')
    eq_(admin.app, None)
    ok_(admin.index_view is not None)
    eq_(admin.index_view._template, 'admin/index.html')

    # Check if default view was added
    eq_(len(admin._views), 1)
    eq_(admin._views[0], admin.index_view)


def test_custom_index_view():
    view = base.AdminIndexView(name='a', category='b', endpoint='c',
                               url='/d', template='e')
    admin = base.Admin(index_view=view)

    eq_(admin.endpoint, 'c')
    eq_(admin.url, '/d')
    ok_(admin.index_view is view)
    eq_(view.name, 'a')
    eq_(view.category, 'b')
    eq_(view._template, 'e')

    # Check if view was added
    eq_(len(admin._views), 1)
    eq_(admin._views[0], view)


def test_base_registration():
    app = Flask(__name__)
    admin = base.Admin(app)

    eq_(admin.app, app)
    ok_(admin.index_view.blueprint is not None)


def test_admin_customizations():
    app = Flask(__name__)
    admin = base.Admin(app, name='Test', url='/foobar', static_url_path='/static/my/admin')
    eq_(admin.name, 'Test')
    eq_(admin.url, '/foobar')
    eq_(admin.index_view.blueprint.static_url_path, '/static/my/admin')

    client = app.test_client()
    rv = client.get('/foobar/')
    eq_(rv.status_code, 200)


def test_baseview_registration():
    admin = base.Admin()

    view = MockView()
    bp = view.create_blueprint(admin)

    # Base properties
    eq_(view.admin, admin)
    ok_(view.blueprint is not None)

    # Calculated properties
    eq_(view.endpoint, 'mockview')
    eq_(view.url, '/admin/mockview')
    eq_(view.name, 'Mock View')

    # Verify generated blueprint properties
    eq_(bp.name, view.endpoint)
    eq_(bp.url_prefix, view.url)
    eq_(bp.template_folder, 'templates')
    eq_(bp.static_folder, view.static_folder)

    # Verify customizations
    view = MockView(name='Test', endpoint='foobar')
    view.create_blueprint(base.Admin())

    eq_(view.name, 'Test')
    eq_(view.endpoint, 'foobar')
    eq_(view.url, '/admin/foobar')

    view = MockView(url='test')
    view.create_blueprint(base.Admin())
    eq_(view.url, '/admin/test')

    view = MockView(url='/test/test')
    view.create_blueprint(base.Admin())
    eq_(view.url, '/test/test')
    
    view = MockView(endpoint='test')
    view.create_blueprint(base.Admin(url='/'))
    eq_(view.url, '/test')
    
    view = MockView(static_url_path='/static/my/test')
    view.create_blueprint(base.Admin())
    eq_(view.blueprint.static_url_path, '/static/my/test')


def test_baseview_urls():
    app = Flask(__name__)
    admin = base.Admin(app)

    view = MockView()
    admin.add_view(view)

    eq_(len(view._urls), 2)


@raises(Exception)
def test_no_default():
    app = Flask(__name__)
    admin = base.Admin(app)
    admin.add_view(base.BaseView())


def test_call():
    app = Flask(__name__)
    admin = base.Admin(app)
    view = MockView()
    admin.add_view(view)
    client = app.test_client()

    rv = client.get('/admin/')
    eq_(rv.status_code, 200)

    rv = client.get('/admin/mockview/')
    eq_(rv.data, 'Success!')

    rv = client.get('/admin/mockview/test/')
    eq_(rv.data, 'Success!')

    # Check authentication failure
    view.allow_call = False
    rv = client.get('/admin/mockview/')
    eq_(rv.data, 'Failure!')


def test_permissions():
    app = Flask(__name__)
    admin = base.Admin(app)
    view = MockView()
    admin.add_view(view)
    client = app.test_client()

    view.allow_access = False

    rv = client.get('/admin/mockview/')
    eq_(rv.status_code, 404)


def test_submenu():
    app = Flask(__name__)
    admin = base.Admin(app)
    admin.add_view(MockView(name='Test 1', category='Test', endpoint='test1'))

    # Second view is not normally accessible
    view = MockView(name='Test 2', category='Test', endpoint='test2')
    view.allow_access = False
    admin.add_view(view)

    ok_('Test' in admin._menu_categories)
    eq_(len(admin._menu), 2)
    eq_(admin._menu[1].name, 'Test')
    eq_(len(admin._menu[1]._children), 2)

    # Categories don't have URLs and they're not accessible
    eq_(admin._menu[1].get_url(), None)
    eq_(admin._menu[1].is_accessible(), False)

    eq_(len(admin._menu[1].get_children()), 1)


def test_delayed_init():
    app = Flask(__name__)
    admin = base.Admin()
    admin.add_view(MockView())
    admin.init_app(app)

    client = app.test_client()

    rv = client.get('/admin/mockview/')
    eq_(rv.data, 'Success!')


def test_multi_instances_init():
    app = Flask(__name__)
    admin = base.Admin(app)

    class ManageIndex(base.AdminIndexView):
        pass
    manage = base.Admin(app, index_view=ManageIndex(url='/manage', endpoint='manage'))


@raises(Exception)
def test_double_init():
    app = Flask(__name__)
    admin = base.Admin(app)
    admin.init_app(app)

def test_nested_flask_views():
    app = Flask(__name__)
    admin = base.Admin(app)

    view = MockMethodView()
    admin.add_view(view)

    client = app.test_client()

    rv = client.get('/admin/mockmethodview/_api/1')
    assert rv.data == 'GET - API1'
    rv = client.put('/admin/mockmethodview/_api/1')
    assert rv.data == 'PUT - API1'
    rv = client.post('/admin/mockmethodview/_api/1')
    assert rv.data == 'POST - API1'
    rv = client.delete('/admin/mockmethodview/_api/1')
    assert rv.data == 'DELETE - API1'

    rv = client.get('/admin/mockmethodview/_api/2')
    assert rv.data == 'GET - API2'
    rv = client.post('/admin/mockmethodview/_api/2')
    assert rv.data == 'POST - API2'
    rv = client.delete('/admin/mockmethodview/_api/2')
    assert rv.status_code == 405
    rv = client.put('/admin/mockmethodview/_api/2')
    assert rv.status_code == 405
