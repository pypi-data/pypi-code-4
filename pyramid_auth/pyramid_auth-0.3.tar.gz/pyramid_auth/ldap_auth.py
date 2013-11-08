from pyramid.authentication import AuthTktAuthenticationPolicy
from paste.util.import_string import eval_import
from pyramid_ldap import get_ldap_connector
import ldap

from .utils import str_to_bool, parse_settings
from .views import BaseLoginView, login_includeme


def validate_ldap(request, login, password):
    """"Validate ldap login and password.

    We just check there is an entry in the ldap.

    :param request: the request
    :type request: pyramid.request
    :param login: the user login
    :type login: str
    :param password: the user password
    :type password: str
    :return: True if there is an entry for the given params in the ldap
    :rtype: bool
    """
    connector = get_ldap_connector(request)
    data = connector.authenticate(login, password)
    if not data:
        return False
    return True


class LdapView(BaseLoginView):

    def get_validate_func(self):
        settings = self.request.registry.settings
        func_str = settings.get('authentication.ldap.validate_function')
        if func_str:
            return eval_import(func_str)
        return validate_ldap


def get_ldap_groups(dn, request):
    """Get the groups set in the ldap and transform them to permission

    .. note:: We try to only get the cn from the group and we prefix the
    permission with 'ldap:'
    """
    connector = get_ldap_connector(request)
    group_list = connector.user_groups(dn)
    if group_list is None:
        return []
    lis = [('ldap:%s' % attrs.get('cn', [dn_])[0]).encode('utf-8')
           for dn_, attrs in group_list]
    return lis


def get_groups(dn, request):
    """Get the groups for the given dn.

    We get the groups from the ldap and we also get from the function set in
    the config. It's usefull, if you have more permission set in the DB or if
    you want to add new logic.
    """
    lis = []
    if request.registry.settings.get('authentication.ldap.groups.filter_tmpl'):
        lis += get_ldap_groups(dn, request)
    callback = request.registry.settings.get('authentication.ldap.callback')
    if callback:
        func = eval_import(callback)
        lis += func(dn, request)
    return lis


def replace_substitution(sub):
    """We can't put %(key)s in the .ini file since the parse try to replace it.
    For this reason we put $key in the config and transform it as dict value
    here.
    """
    def func(s):
        return s.replace('$%s' % sub, '%%(%s)s' % sub)
    return func


SETTINGS = {
    'cookie': [
        ('secret', None, True, None),
        ('callback', eval_import, False, get_groups),
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
    ],
    'setup': [
        ('uri', None, True, None),
        ('bind', None, False, None),
        ('passwd', None, False, ''),
        ('pool_size', int, False, None),
        ('retry_max', int, False, None),
        ('retry_delay', float, False, None),
        ('use_tls', str_to_bool, False, None),
        ('timeout', int, False, None),
        ('use_pool', str_to_bool, False, None),
    ],
    'login': [
        ('base_dn', None, True, None),
        ('filter_tmpl', replace_substitution('login'), True, None),
        ('scope', eval_import, False, None),
        ('cache_period', int, False, None),
    ],
    'groups': [
        ('base_dn', None, True, None),
        ('filter_tmpl', replace_substitution('userdn'), True, None),
        ('scope', eval_import, False, None),
        ('cache_period', int, False, 0),
    ]
}


def includeme(config):
    settings = config.registry.settings
    prefix = 'authentication.ldap'
    config.set_authentication_policy(
        AuthTktAuthenticationPolicy(
            **parse_settings(settings, SETTINGS, 'cookie', prefix)
        )
    )

    config.ldap_setup(**parse_settings(settings,
                                       SETTINGS,
                                       'setup',
                                       prefix))
    config.ldap_set_login_query(**parse_settings(settings,
                                                 SETTINGS,
                                                 'login',
                                                 prefix))
    config.ldap_set_groups_query(**parse_settings(settings,
                                                  SETTINGS,
                                                  'groups',
                                                  prefix))

    login_includeme(LdapView, config)
