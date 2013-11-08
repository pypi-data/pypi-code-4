from pyramid.authentication import RemoteUserAuthenticationPolicy
from paste.util.import_string import eval_import

from .utils import str_to_bool, parse_settings
from.views import base_includeme


SETTINGS = {
    'remote_user': [
        ('environ_key', None, False, None),
        ('debug', str_to_bool, False, None),
        ('callback', eval_import, False, None),
    ]
}


def includeme(config):
    settings = parse_settings(config.registry.settings, SETTINGS,
                              'remote_user', 'authentication')
    config.set_authentication_policy(
        RemoteUserAuthenticationPolicy(
            **settings
        )
    )
    base_includeme(config)
