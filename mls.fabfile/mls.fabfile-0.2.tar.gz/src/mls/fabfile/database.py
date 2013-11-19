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
    upload_zodb(start_when_done=False)
    upload_blob()


@api.task
@api.roles('database')
def upload_zodb(start_when_done=True):
    """Upload ZODB part of Zope's data to the server."""
    config = utils.mls_config()
    folder = config.get('zeo', {}).get('dir') or err('Folder must be set!')
    user = config.get('user') or err('MLS user must be set!')

    if not confirm('This will overwrite your remote Data.fs. Are you sure you '
                   'want to continue?', default=False):
        api.abort('ZODB upload cancelled.')

    api.sudo('mkdir -p /tmp/upload', user=user)

    api.put('var/filestorage/Data.fs', '/tmp/upload/Data.fs', use_sudo=True)
    api.sudo('chown %s /tmp/upload/Data.fs' % user)

    utils.supervisorctl(command='stop', service='zeoserver')
    with api.settings(sudo_user=user):
        with api.cd(folder):
            # Backup current Data.fs.
            if exists('var/filestorage/Data.fs'):
                api.sudo('mv var/filestorage/Data.fs var/filestorage/Data.fs.bak')
            api.sudo('mv /tmp/upload/Data.fs var/filestorage/Data.fs')

    if start_when_done:
        utils.supervisorctl(command='start', service='zeoserver')


@api.task
@api.roles('database')
def upload_blob(start_when_done=True):
    """Upload blob part of Zope's data to the server."""
    config = utils.mls_config()
    folder = config.get('zeo', {}).get('dir') or err('Folder must be set!')
    user = config.get('user') or err('MLS user must be set!')

    if not confirm('This will overwrite your remote blob files. Are you sure '
                   'you want to continue?', default=False):
        api.abort('Blob upload cancelled.')

    api.sudo('mkdir -p /tmp/upload', user=user)

    with api.lcd('var'):
        api.local('tar czf blobstorage_upload.tgz blobstorage')
        api.put('blobstorage_upload.tgz', '/tmp/upload/blobstorage.tgz', use_sudo=True)

    api.sudo('chown %s /tmp/upload/blobstorage.tgz' % user)
    with api.cd('/tmp/upload'):
        api.sudo('tar xzf blobstorage.tgz', user=user)

    utils.supervisorctl(command='stop', service='zeoserver')
    with api.settings(sudo_user=user):
        with api.cd(folder):
            # Backup current blob files.
            if exists('var/blobstorage'):
                api.sudo('mv var/blobstorage var/blobstorage_bak')
            api.sudo('mv /tmp/upload/blobstorage var')

    if start_when_done:
        utils.supervisorctl(command='start', service='zeoserver')


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
