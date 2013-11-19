# -*- coding: utf-8 -*-
"""Manage MLS database components."""

import os
from fabric import api
from fabric.contrib.console import confirm
from fabric.contrib.files import exists
from mls.fabfile import utils
from mls.fabfile.exceptions import err


@api.task
@api.roles('database')
def restart():
    """Restart the database component."""
    utils.supervisorctl(command='restart', service='zeoserver')


@api.task
@api.roles('database')
def download_data():
    """Download the database files from the server."""
    download_zodb()
    download_blobs()


@api.task
@api.roles('database')
def download_zodb():
    """Download ZODB part of Zope's data from the server."""
    config = utils.mls_config()
    folder = config.get('zeo', {}).get('dir') or err('Folder must be set!')
    user = config.get('user') or err('MLS user must be set!')

    if not confirm('This will overwrite your local Data.fs. Are you sure you '
                   'want to continue?'):
        api.abort('ZODB download cancelled.')

    api.local('mkdir -p var/filestorage')

    # Backup current Data.fs.
    if os.path.exists('var/filestorage/Data.fs'):
        api.local('mv var/filestorage/Data.fs var/filestorage/Data.fs.bak')

    with api.settings(sudo_user=user):

        # Remove temporary Data.fs file from previous downloads.
        if exists('/tmp/Data.fs', use_sudo=True):
            api.sudo('rm -rf /tmp/Data.fs')

        # Downlaod Data.fs from server.
        with api.cd(folder):
            api.sudo('rsync -a var/filestorage/Data.fs /tmp/Data.fs')
            api.get('/tmp/Data.fs', 'var/filestorage/Data.fs')


@api.task
@api.roles('database')
def download_blobs():
    """Download blob part of Zope's data from the server."""
    config = utils.mls_config()
    folder = config.get('zeo', {}).get('dir') or err('Folder must be set!')
    user = config.get('user') or err('MLS user must be set!')

    if not confirm('This will overwrite your local blob files. Are you sure '
                   'you want to continue?'):
        api.abort('Blob download cancelled.')

    # Remove local blob files backup.
    if os.path.exists('var/blobstorage_bak'):
        api.local('rm -rf var/blobstorage_bak')

    # Backup current blob files.
    if os.path.exists('var/blobstorage'):
        api.local('mv var/blobstorage var/blobstorage_bak')

    with api.settings(sudo_user=user):

        # Remove temporary blob files from previous downloads.
        if exists('/tmp/blobstorage', use_sudo=True):
            api.sudo('rm -rf /tmp/blobstorage')

        if exists('/tmp/blobstorage.tgz', use_sudo=True):
            api.sudo('rm -rf /tmp/blobstorage.tgz')

        # Download blob files from server.
        with api.cd(folder):
            api.sudo('rsync -a ./var/blobstorage /tmp/')

        with api.cd('/tmp'):
            api.sudo('tar czf blobstorage.tgz blobstorage')
            api.get('/tmp/blobstorage.tgz', './var/blobstorage.tgz')

        with api.lcd('var'):
            api.local('tar xzf blobstorage.tgz')


@api.task
@api.roles('database')
def upload_data():
    """Upload the database files to the server."""
    raise NotImplementedError


@api.task
@api.roles('database')
def upload_zodb():
    """Upload ZODB part of Zope's data to the server."""
    raise NotImplementedError


@api.task
@api.roles('database')
def upload_blob():
    """Upload blob part of Zope's data to the server."""
    raise NotImplementedError


@api.task
@api.roles('database')
def backup():
    """Perform a backup of Zope's data on the server."""
    raise NotImplementedError


@api.task
@api.roles('database')
def restore():
    """Restore an existing backup of Zope's data on the server."""
    raise NotImplementedError
