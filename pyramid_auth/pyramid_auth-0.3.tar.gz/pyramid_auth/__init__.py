from pyramid.authorization import ACLAuthorizationPolicy
from paste.util.import_string import eval_import


def includeme(config):
    settings = config.registry.settings
    policy = settings.get('authentication.policy') or 'cookie'

    if policy not in ['cookie', 'remote_user', 'ldap']:
        raise Exception('Policy not supported: %s' % policy)

    mod = eval_import('pyramid_auth.%s_auth' % policy)
    config.set_authorization_policy(ACLAuthorizationPolicy())
    mod.includeme(config)

    sqladmin_dir = 'pyramid_auth:templates'

    if 'mako.directories' not in settings:
        settings['mako.directories'] = []

    if type(settings['mako.directories']) is list:
        settings['mako.directories'] += [sqladmin_dir]
    else:
        settings['mako.directories'] += '\n%s' % sqladmin_dir
