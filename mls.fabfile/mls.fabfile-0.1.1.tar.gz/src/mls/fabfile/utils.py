# -*- coding: utf-8 -*-

from chef import autoconfigure, Search
from datetime import datetime
from fabric import api
from mls.fabfile.exceptions import err


def mls_config():
    """Get the MLS user for the current node."""
    chef_api = autoconfigure()
    for node in Search('node', 'ipaddress:%s' % api.env.host, api=chef_api):
        try:
            return node.object['mls']
        except KeyError:
            return {}


def backup_dev_packages(folder=None, user=None):
    """Backup the development packages."""
    config = mls_config()
    folder = folder or config.get('app', {}).get('dir') or err('Folder must be set!')
    user = user or config.get('user') or err('MLS user must be set!')
    with api.settings(sudo_user=user):
        # Backup buildout src packages.
        with api.cd(folder):
            now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            backup_folder = 'src_backups/%s' % now
            api.sudo('mkdir -p %s' % backup_folder)
            api.sudo('mv ./src/* %s' % backup_folder)


def update_dev_packes(folder=None, user=None):
    """Update the development packages."""
    config = mls_config()
    folder = folder or config.get('app', {}).get('dir') or err('Folder must be set!')
    user = user or config.get('user') or err('MLS user must be set!')
    with api.settings(sudo_user=user):
        # Update buildout src packages.
        with api.cd(folder):
            api.sudo('./bin/develop up -f')


def run_buildout(folder=None, user=None):
    """Run the buildout."""
    config = mls_config()
    folder = folder or config.get('app', {}).get('dir') or err('Folder must be set!')
    user = user or config.get('user') or err('MLS user must be set!')
    with api.settings(sudo_user=user):
        # Run buildout.
        with api.cd(folder):
            api.sudo('./bin/buildout')


def supervisorctl(command=None, service=None):
    """Control supervisor services."""
    api.sudo('supervisorctl %s %s' % (command, service), warn_only=True)
