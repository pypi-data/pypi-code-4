from pyramid.view import view_config
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPForbidden,
)
from pyramid.security import (
    unauthenticated_userid,
    remember,
    forget,
)
from urllib import urlencode
import tw2.core as twc

from . import forms


class BaseView(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def forbidden(self):
        return {}


class BaseLoginView(BaseView):

    def get_validate_func(self):
        raise NotImplementedError

    def _get_next_location(self):
        login_url = self.request.route_url('login')
        referrer = self.request.url
        if referrer == login_url:
            referrer = '/'
        return self.request.params.get('next', referrer)

    def login(self):
        LoginForm = forms.create_login_form(self.request,
                                            self.get_validate_func())
        widget = LoginForm().req()
        if self.request.method == 'POST':
            try:
                data = widget.validate(self.request.POST)
                headers = remember(self.request, data['login'])
                return HTTPFound(location=self._get_next_location(),
                                 headers=headers)
            except twc.ValidationError, e:
                widget = e.widget
        return dict(widget=widget)

    def logout(self):
        headers = forget(self.request)
        location = self.request.params.get('next', self.request.application_url)
        return HTTPFound(location=location, headers=headers)

    def forbidden_redirect(self):
        if unauthenticated_userid(self.request):
            # The user is logged but doesn't have the right permission
            location = self.request.route_url('forbidden')
        else:
            login_url = self.request.route_url('login')
            location = '%s?%s' % (login_url, urlencode({'next': self.request.url}))
        return HTTPFound(location=location)


def base_includeme(config):
    config.add_view(
        BaseView,
        attr='forbidden',
        context=HTTPForbidden,
        renderer='auth/forbidden.mak')


def login_includeme(ViewClass, config):
    config.add_view(
        ViewClass,
        attr='forbidden_redirect',
        context=HTTPForbidden)

    config.add_route(
        'forbidden',
        '/forbidden',
    )
    config.add_view(
        ViewClass,
        attr='forbidden',
        route_name='forbidden',
        renderer='auth/forbidden.mak')

    config.add_route(
        'login',
        '/login',
    )
    config.add_view(
        ViewClass,
        attr='login',
        route_name='login',
        renderer='auth/login.mak')

    config.add_route(
        'logout',
        '/logout',
    )
    config.add_view(
        ViewClass,
        attr='logout',
        route_name='logout')
