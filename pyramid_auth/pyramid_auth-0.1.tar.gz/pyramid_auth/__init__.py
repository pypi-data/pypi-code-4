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
import tw2.forms as twf, tw2.core as twc
from paste.util.import_string import eval_import


class UserExists(twc.Validator):
    """Validate the user exists in the DB. It's used when we want to
    authentificate it.
    """
    __unpackargs__ = ('login', 'password', 'validate_func')
    msgs = {
        'mismatch': 'Please check your posted data.',
    }

    def _validate_python(self, value, state):
        super(UserExists, self)._validate_python(value, state)
        login = value[self.login]
        password = value[self.password]
        for v in [login, password]:
            try:
                if issubclass(v, twc.validation.Invalid):
                    # No need to validate the password of the user, the login
                    # or password are invalid
                    return
            except TypeError:
                pass

        if not self.validate_func(login, password):
            raise twc.ValidationError('mismatch', self)


def create_login_form(settings):
    func_str = settings.get('pyramid_auth.validate_function')
    if not func_str:
        raise AttributeError, ('pyramid_auth.validate_function '
                               'is not defined in the conf')
    func = eval_import(func_str)

    class LoginForm(twf.TableForm):
        login = twf.TextField(validator=twc.Validator(required=True))
        password = twf.PasswordField(validator=twc.Validator(required=True))
        submit = twf.SubmitButton(id='submit', value='Login')

        validator = UserExists(login='login',
                               password='password',
                               validate_func=func)
    return LoginForm


@view_config(route_name='login', renderer='auth/login.mak')
def login(context, request):
    login_url = request.route_url('login')
    referrer = request.url
    if referrer == login_url:
        referrer = '/'
    next = request.params.get('next', referrer)

    LoginForm = create_login_form(request.registry.settings)
    widget = LoginForm().req()
    if request.method == 'POST':
        try:
            data = widget.validate(request.POST)
            headers = remember(request, data['login'])
            return HTTPFound(location = next,
                             headers = headers)
        except twc.ValidationError, e:
            widget = e.widget

    return dict(
        widget=widget,
        )


@view_config(route_name='logout')
def logout(context, request):
    headers = forget(request)
    location = request.params.get('next', request.application_url)
    return HTTPFound(location=location, headers=headers)


@view_config(route_name='forbidden', renderer='auth/forbidden.mak')
def forbidden(context, request):
    return {}


def forbidden_redirect(context, request):
    if unauthenticated_userid(request):
        # The user is logged but doesn't have the right permission
        location = request.route_url('forbidden')
    else:
        login_url = request.route_url('login')
        location = '%s?%s' % (login_url, urlencode({'next': request.url}))
    return HTTPFound(location=location)


def includeme(config):
    sqladmin_dir = 'pyramid_auth:templates'
    if type(config.registry.settings['mako.directories']) is list:
        config.registry.settings['mako.directories'] += [sqladmin_dir]
    else:
        config.registry.settings['mako.directories'] += '\n%s' % sqladmin_dir

    config.add_view(
        forbidden_redirect,
        context=HTTPForbidden,
    )

    config.add_route(
        'forbidden',
        '/forbidden',
    )

    config.add_route(
        'login',
        '/login',
    )

    config.add_route(
        'logout',
        '/logout',
    )
    config.scan(__name__)
