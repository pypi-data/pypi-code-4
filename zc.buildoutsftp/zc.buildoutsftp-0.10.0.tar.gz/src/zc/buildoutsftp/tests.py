##############################################################################
#
# Copyright (c) Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
from zope.testing import setupstack
import doctest
import mimetypes
import mock
import os
import paramiko
import unittest

def side_effect(mock, f=None):
    if f is None:
        return lambda f: side_effect(mock, f)
    mock.side_effect = f

def hack_path(path):
    if path.startswith('/etc/'):
        return path[1:]
    return path

def setup(test):
    globs = test.globs

    mimetypes.init()

    setupstack.setUpDirectory(test)
    setupstack.context_manager(test, mock.patch('urllib2.install_opener'))
    setupstack.context_manager(test, mock.patch('urllib2.build_opener'))
    setupstack.context_manager(
        test, mock.patch.dict(os.environ, values=dict(HOME=os.getcwd())))

    original_exists = os.path.exists
    @side_effect(setupstack.context_manager(test, mock.patch('os.path.exists')))
    def exists(path):
        return original_exists(hack_path(path))

    original_open = open
    setupstack.context_manager(
        test, mock.patch.dict(__builtins__, values=dict(open=mock.MagicMock())))
    @side_effect(__builtins__['open'])
    def _open(path, *args, **kw):
        return original_open(hack_path(path), *args, **kw)

    setupstack.context_manager(test, mock.patch('getpass.getuser')
                               ).return_value = 'testuser'

    globs['agent_keys'] = agent_keys = []
    @side_effect(
        setupstack.context_manager(
            test, mock.patch('paramiko.Agent')).return_value.get_keys)
    def get_keys():
        return agent_keys

    globs['creds'] = creds = {
        # {(addr, user} -> dict(host_key, user_key}
        (('example.com', 22), 'testuser'): dict(
            host_key = paramiko.RSAKey.generate(1024),
            user_key = paramiko.RSAKey.generate(1024),
            ),
        }

    class Transport:

        def __init__(self, addr):
            self.addr = addr

        def connect(self, username, pkey):
            try:
                key = creds[(self.addr, username)]['user_key']
                if pkey == key:
                    self.username = username
                    return
            except KeyError:
                pass
            raise paramiko.AuthenticationException()

        def close(self):
            pass

        def get_remote_server_key(self):
            return creds.get((self.addr, self.username))['host_key']

    @side_effect(
        setupstack.context_manager(
            test, mock.patch('paramiko.Transport')))
    def transport(addr):
        return Transport(addr)

    globs['server_files'] = {} # addr -> path
    class SFTPClient:

        def __init__(self, transport):
            self.addr = transport.addr

        def _path(self, path):
            assert path.startswith(os.path.sep)
            base = '%s:%s' % self.addr
            path = path[1:]
            if path:
                return os.path.join(base, path)
            else:
                return base

        def stat(self, path):
            return os.stat(self._path(path))

        def listdir(self, path):
            return os.listdir(self._path(path))

        def open(self, path):
            return original_open(self._path(path))

    @side_effect(
        setupstack.context_manager(
            test, mock.patch('paramiko.SFTPClient.from_transport')))
    def from_transport(trans):
        return SFTPClient(trans)

    os.makedirs(os.path.join('example.com:22', 'data', 'moredata'))
    with open(os.path.join('example.com:22', 'data', 'index.html'), 'w') as f:
        f.write('Hi world!\n')

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'main.test', setUp=setup, tearDown=setupstack.tearDown),
        ))

