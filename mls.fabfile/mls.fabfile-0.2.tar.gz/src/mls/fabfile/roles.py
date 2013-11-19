# -*- coding: utf-8 -*-
"""Manage chef roles."""

from chef import autoconfigure, Role
from fabric import api
from fabric.colors import green, red
from mls.fabfile.exceptions import missing_env


def _check_role(role, roles=None):
    """Check if a given role is available on the chef server."""
    if not roles:
        chef_api = autoconfigure()
        roles = Role.list(api=chef_api)
    return role in roles


def _required_roles():
    """Get a list of required roles."""
    role_database = api.env.get('role_database')
    role_database = role_database or missing_env('role_database')
    role_frontend = api.env.get('role_frontend')
    role_frontend = role_frontend or missing_env('role_frontend')
    role_staging = api.env.get('role_staging')
    role_staging = role_staging or missing_env('role_staging')
    role_worker = api.env.get('role_worker')
    role_worker = role_worker or missing_env('role_worker')

    return {
        'role_database': role_database,
        'role_frontend': role_frontend,
        'role_staging': role_staging,
        'role_worker': role_worker,
    }

@api.task
def check():
    """Check if the required roles are available."""
    chef_api = autoconfigure()
    chef_roles = Role.list(api=chef_api)

    for role in _required_roles().values():
        if _check_role(role, chef_roles):
            print(green('Role %s available.') % role)
        else:
            print(red('Role %s NOT available.') % role)


@api.task
def create_missing():
    """Create missing roles on the chef server."""
    chef_api = autoconfigure()
    required = _required_roles()
    domain = api.env.get('domain', 'example.com')

    # Create the role_database.
    if not _check_role(required.get('role_database')):
        name = required.get('role_database')
        description = 'ZEO Server for %s.' % domain
        run_list = (
            "role[mls_zeoserver]",
        )
        default_attributes = {
            'domain': domain,
        }

        Role.create(
            name,
            api=chef_api,
            description=description,
            run_list=run_list,
            default_attributes=default_attributes,
        )
        print(green('Created role %s') % name)

    # Create the role_frontend.
    if not _check_role(required.get('role_frontend')):
        name = required.get('role_frontend')
        description = 'Frontend Server for %s.' % domain
        run_list = (
            "role[mls_loadbalancer]",
        )
        default_attributes = {
            'domain': domain,
            'haproxy': {
                'app_server_role': required.get('role_worker'),
            },
            'mls': {
                'domain': '.'.join(['mls', domain]),
            },
        }

        Role.create(
            name,
            api=chef_api,
            description=description,
            run_list=run_list,
            default_attributes=default_attributes,
        )
        print(green('Created role %s') % name)

    # Create the role_worker.
    if not _check_role(required.get('role_worker')):
        name = required.get('role_worker')
        description = 'Application Worker for %s.' % domain
        run_list = (
            "role[mls_application]",
        )
        default_attributes = {
            'domain': domain,
            'mls': {
                'customizations': api.env.get('mls_customizations', []),
                'policy': {
                    'enabled': api.env.get('mls_policy_enabled') and 'true' or 'false',
                    'package': api.env.get('mls_policy_package', ''),
                    'package_url': api.env.get('mls_policy_package_url', ''),
                },
                'zeo_role': required.get('role_database'),
            },
        }

        Role.create(
            name,
            api=chef_api,
            description=description,
            run_list=run_list,
            default_attributes=default_attributes,
        )
        print(green('Created role %s') % name)

    # Create the role_staging.
    if not _check_role(required.get('role_staging')):
        name = required.get('role_staging')
        description = 'Staging system for %s.' % domain
        run_list = (
            "role[%s]" % required.get('role_database'),
            "role[%s]" % required.get('role_worker'),
            "role[%s]" % required.get('role_frontend'),
        )
        default_attributes = {
            'domain': domain,
            'haproxy': {
                'app_server_role': name,
            },
            'mls': {
                'domain': '.'.join(['staging', domain]),
                'zeo_role': name,
            },
        }

        Role.create(
            name,
            api=chef_api,
            description=description,
            run_list=run_list,
            default_attributes=default_attributes,
        )
        print(green('Created role %s') % name)
