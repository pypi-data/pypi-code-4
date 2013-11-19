# -*- coding: utf-8 -*-
"""Environment definitions."""

from chef.fabric import chef_roledefs
from fabric import api

__all__ = [
    'development',
    'production',
    'staging',
]


def update_roledefs(environment):
    """Update Fabric's role definitions with our chef based roles.

    :param environment: The chef environment to search for.
    :type environment: string
    """
    roledefs = chef_roledefs(
        hostname_attr=['ipaddress'],
        environment=environment,
    )
    role_database = api.env.get('role_database', None)
    if role_database:
        api.env.roledefs['database'] = roledefs.get(role_database)

    role_frontend = api.env.get('role_frontend')
    if role_frontend:
        api.env.roledefs['frontend'] = roledefs.get(role_frontend)

    role_staging = api.env.get('role_staging')
    if role_staging:
        api.env.roledefs['staging'] = roledefs.get(role_staging)

    role_worker = api.env.get('role_worker')
    if role_worker:
        api.env.roledefs['worker'] = roledefs.get(role_worker)


@api.task
def development():
    """Work locally with vagrant."""
    # Change the default user to 'vagrant'.
    result = api.local('vagrant ssh-config | grep IdentityFile', capture=True)
    api.env.key_filename = result.replace('"', '').split()[1]
    api.env.user = 'vagrant'

    # Connect to the port-forwarded ssh.
    api.env.hosts = ['127.0.0.1:2222']

    # Set role definitions for vagrant.
    api.env.roledefs = {
        'worker': ['127.0.0.1:2222', ],
        'frontend': ['127.0.0.1:2222', ],
        'database': ['127.0.0.1:2222', ],
    }


@api.task
def staging():
    """Work with the staging environment."""
    update_roledefs('staging')


@api.task
def production():
    """Work with the production environment."""
    update_roledefs('production')
