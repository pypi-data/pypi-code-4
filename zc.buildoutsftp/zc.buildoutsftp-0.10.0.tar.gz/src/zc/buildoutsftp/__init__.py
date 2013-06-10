##############################################################################
#
# Copyright (c) 2006, 2012 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import atexit
import cStringIO
import getpass
import logging
import mimetypes
import os
import paramiko
import re
import stat
import sys
import urllib
import urllib2

logger = logging.getLogger(__name__)

def install(buildout=None):
    urllib2.install_opener(urllib2.build_opener(SFTPHandler))
    logging.getLogger('paramiko').setLevel(logger.getEffectiveLevel()+10)

def unload(buildout=None):
    # no uninstall_opener. Screw it. :)
    cleanup()

parse_url_host = re.compile(
    '(?:' '([^@:]+)(?::([^@]*))?@' ')?'
    '([^:]*)(?::(\d+))?$').match

def deunixpath(path):
    return os.path.join(*path.split('/'))

_configs = None
def _get_config(host):
    global _configs
    if _configs is None:
        _configs = []
        for path in (
            deunixpath('/etc/ssh/ssh_config'), deunixpath('/etc/ssh_config'),
            os.path.expanduser(deunixpath('~/.ssh/config')),
            ):
            if os.path.exists(path):
                config = paramiko.SSHConfig()
                with open(path) as f:
                    config.parse(f)
                _configs.append(config)

    r = {}
    for config in _configs:
        r.update(config.lookup(host))

    return r

if sys.platform == 'win32':
    import _winreg
    parse_reg_key_name = re.compile('(rsa|dss)2?@22:(\S+)$').match
    def _get_host_keys(config):
        regkey = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER,
                                 r'Software\SimonTatham\PuTTY\SshHostKeys',
                                 )
        keys = paramiko.HostKeys()
        i = 0
        while 1:
            try:
                name, value, type_ = _winreg.EnumValue(regkey, i)
                i += 1
                value = [long(v, 16) for v in value.split(',')]
                ktype, host = parse_reg_key_name(name).groups()
                if ktype == 'rsa':
                    key = paramiko.RSAKey(vals=value)
                if ktype == 'dss':
                    key = paramiko.DSSKey(vals=value)
                keys.add(host, 'ssh-'+ktype, key)
            except WindowsError:
                break

        return keys

else:
    def _get_host_keys(config):
        user_host_keys = os.path.expanduser('~/.ssh/known_hosts')
        if os.path.exists(user_host_keys):
            host_keys = paramiko.HostKeys(user_host_keys)
        else:
            host_keys = {}
        global_host_keys = config.get('globalknownhostsfile')
        if not global_host_keys:
            for path in ('/etc/ssh/ssh_known_hosts',
                         '/etc/ssh_known_hosts'):
                if os.path.exists(path):
                    global_host_keys = path
                    break
        if global_host_keys:
            host_keys.update(paramiko.HostKeys(global_host_keys))
        return host_keys

class Result:

    def __init__(self, fp, url, info, trans):
        self._fp = fp
        self.url = url
        self.headers = info
        self.__trans = trans

    def geturl(self):
        return self.url

    def info(self):
        return self.headers

    def __getattr__(self, name):
        return getattr(self._fp, name)

def _open_key(key_path):
    key = None
    if os.path.exists(key_path):
        try:
            key = paramiko.RSAKey.from_private_key_file(key_path)
        except paramiko.SSHException:
            try:
                key = paramiko.DSSKey.from_private_key_file(key_path)
            except paramiko.SSHException:
                logger.error('Invalid key file: %s', key_path)
    return key

_connection_pool = {}

def cleanup():
    for k in list(_connection_pool):
        trans = _connection_pool.pop(k)
        if trans is not False:
            trans.close()

    global _configs
    _configs = None

atexit.register(cleanup)

class SFTPHandler(urllib2.BaseHandler):

    def sftp_open(self, req):
        host = req.get_host()
        if not host:
            raise IOError, ('sftp error', 'no host given')

        parsed = parse_url_host(host)
        if not parsed:
            raise IOError, ('sftp error', 'invalid host', host)

        user, pw, host, port = parsed.groups()

        host = urllib.unquote(host or '')

        config = _get_config(host)

        host_keys = _get_host_keys(config).get(host)
        if host_keys is None:
            raise paramiko.AuthenticationException("No stored host key", host)

        if user:
            user = urllib.unquote(user)
        else:
            user = config.get('user', getpass.getuser())

        if port:
            port = int(port)
        else:
            port = 22

        if pw:
            pw = urllib.unquote(pw)


        if pw is not None:
            pool_key = (host, port, user, pw)
            trans = _connection_pool.get(pool_key)
            if trans is None:
                trans = paramiko.Transport((host, port))
                try:
                    trans.connect(username=user, password=pw)
                except paramiko.AuthenticationException:
                    trans.close()
                    raise
        else:
            keys = list(paramiko.Agent().get_keys())
            IdentityFile = config.get('identityfile')
            if IdentityFile:
                if isinstance(IdentityFile, basestring):
                    IdentityFile = [IdentityFile]
                for key_path in IdentityFile:
                    key = _open_key(os.path.expanduser(key_path))
                    if key is None:
                        logger.error('IdentityFile, %s, does not exist', key)
                    else:
                        keys.insert(0, key)
            else:
                for path in (
                    '~/.ssh/identity', '~/.ssh/id_rsa', '~/.ssh/id_dsa'):
                    path = deunixpath(path)
                    key = _open_key(os.path.expanduser(path))
                    if key is not None:
                        keys.insert(0, key)

            for key in keys:
                pool_key = (host, port, str(key))
                trans = _connection_pool.get(pool_key)
                if trans is not None:
                    if trans is False:
                        # Failed previously, so don't try again
                        continue
                    break
                trans = paramiko.Transport((host, port))
                try:
                    trans.connect(username=user, pkey=key)
                    break
                except paramiko.AuthenticationException:
                    trans.close()
                    _connection_pool[pool_key] = False
            else:
                raise paramiko.AuthenticationException(
                    "Authentication failed.")

        if pool_key not in _connection_pool:
            # Check host key
            remote_server_key = trans.get_remote_server_key()
            host_key = host_keys.get(remote_server_key.get_name())
            if host_key != remote_server_key:
                raise paramiko.AuthenticationException(
                    "Remote server authentication failed.", host)
            _connection_pool[pool_key] = trans

        sftp = paramiko.SFTPClient.from_transport(trans)

        path = req.get_selector()
        url = req.get_full_url()
        logger.debug('sftp get: %s', url)
        mode = sftp.stat(path).st_mode
        if stat.S_ISDIR(mode):
            if logger.getEffectiveLevel() < logging.DEBUG:
                logger.log(1, "Dir %s:\n  %s\n",
                           path, '\n  '.join(sftp.listdir(path)))

            return Result(
                cStringIO.StringIO('\n'.join([
                    ('<a href="%s/%s">%s</a><br />'
                     % (url, x, x)
                     )
                    for x in sorted(sftp.listdir(path))
                    ])),
                url, {'content-type': 'text/html'}, trans)
        else:
            mtype = mimetypes.guess_type(url)[0]
            if mtype is None:
                mtype = 'application/octet-stream'
            return Result(sftp.open(path), url, {'content-type': mtype},
                          trans)

