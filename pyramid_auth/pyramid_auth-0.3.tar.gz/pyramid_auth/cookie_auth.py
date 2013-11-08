from pyramid.authentication import AuthTktAuthenticationPolicy
from paste.util.import_string import eval_import

from .utils import str_to_bool, parse_settings
from .views import BaseLoginView, login_includeme


class CookieView(BaseLoginView):

    def get_validate_func(self):
        settings = self.request.registry.settings
        key = 'authentication.cookie.validate_function'
        func_str = settings.get(key)
        if not func_str:
            raise AttributeError('%s is not defined.' % key)
        return eval_import(func_str)


SETTINGS = {
    'cookie': [
        ('secret', None, True, None),
        ('callback', eval_import, False, None),
        ('cookie_name', None, False, None),
        ('secure', str_to_bool, False, None),
        ('include_ip', str_to_bool, False, None),
        ('timeout', int, False, None),
        ('reissue_time', int, False, None),
        ('max_age', int, False, None),
        ('path', None, False, None),
        ('http_only', str_to_bool, False, None),
        ('wild_domain', str_to_bool, False, None),
        ('debug', str_to_bool, False, None),
        ('hashalg', None, False, 'sha512')
    ]
}


def includeme(config):
    settings = parse_settings(config.registry.settings, SETTINGS, 'cookie',
                              'authentication')
    config.set_authentication_policy(
        AuthTktAuthenticationPolicy(
            **settings
        )
    )
    login_includeme(CookieView, config)
