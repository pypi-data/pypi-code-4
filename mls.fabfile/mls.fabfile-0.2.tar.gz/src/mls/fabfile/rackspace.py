# -*- coding: utf-8 -*-
"""Manage servers at Rackspace."""

from chef import autoconfigure
from chef.search import Search
from fabric import api
from fabric.colors import red


def create(**params):
    """Create a new server on Rackspace."""
    COMMAND_CREATE = ' '.join([
        'knife rackspace server create',
        '-S %(servername)s',
        '-N %(nodename)s',
        '-f %(flavor)s',
        '-I %(image)s',
        '-r role[rackspace],%(runlist)s',
        '-E %(environment)s',
    ])

    chef_api = autoconfigure()
    query = 'name:%(nodename)s AND chef_environment:%(environment)s' % params
    if len(Search('node', query, api=chef_api)) > 0:
        api.abort(
            'Server "%(nodename)s" already exists in environment '
            '"%(environment)s".' % params)

    api.local(COMMAND_CREATE % params)


def remove(**params):
    """Remove an existing server on Rackspace."""
    COMMAND_LIST = 'knife rackspace server list | grep %s'
    COMMAND_DELETE = 'knife rackspace server delete %s --purge'

    chef_api = autoconfigure()
    query = 'role:%(role)s AND chef_environment:%(environment)s' % params
    nodes = sorted([node.object.name for node in Search('node', query, api=chef_api)])

    print(red('Available nodes:'))
    print(red(', '.join(nodes)))

    client = api.prompt('Which node should be removed?')
    result = api.local(COMMAND_LIST % client, capture=True)
    server_id = result.split()[0]
    api.local(COMMAND_DELETE % server_id)


def next_client_number(**params):
    chef_api = autoconfigure()
    query = 'role:%(rolename)s AND chef_environment:%(environment)s' % params
    nodes = sorted([
        node.object.name for node in Search('node', query, api=chef_api)
    ])
    if len(nodes) < 1:
        return 1
    last = nodes[-1]
    number = last.split('-')[-1]
    try:
        number = int(number)
    except ValueError, e:
        raise e
    else:
        return number + 1
