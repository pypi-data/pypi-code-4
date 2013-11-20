#!/usr/bin/env python
#-*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import getpass
import os
import re
import sys
import shutil
from binascii import hexlify
try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser
from zipfile import ZipFile
from rarfile import RarFile
from glob import iglob

from pyasn1.codec.der import decoder
from cprocsp import csp, cryptoapi

from . import KeysetException

if sys.version_info >= (3,):
    ord = lambda x: x
    _decode = lambda x: str(x, sys.getdefaultencoding())
    unicode = str
else:
    _decode = unicode


def _rarsplit(fn):
    res = re.split(r'[\\/]', fn, maxsplit=1)
    if len(res) == 1:
        res.insert(0, '')
    return res


def _rarbase(fn):
    m = re.search(r'[\\/](.*?)$', fn)
    if m:
        return m.group(1)
    return fn


def _cert_info(certdata):
    # return cryptoapi.cert_info(certdata)
    tc = csp.Cert(certdata)
    ci = csp.CertInfo(tc)
    return dict(
        name=_decode(ci.name()),
        thumb=_decode(hexlify(tc.thumbprint())),
        issuer=_decode(ci.issuer()),
        serial=':'.join(hex(ord(x))[2:] for x in
                        reversed(ci.serial())),
    )


def _ensure(flag, msg, exc=KeysetException):
    if not flag:
        raise exc(msg)


class hdimage(object):
    """Incapsulation of keyset stored on hdimage.
    WARNING:
    ----------------------------------------------------------------------
    Not thread-safe yet, avoid running multiple operations simultaneously!
    ----------------------------------------------------------------------

    """

    _names = set(('primary2.key', 'header.key', 'primary.key', 'masks.key',
                 'masks2.key', 'name.key',))
    _keyspecs = ('AT_SIGNATURE', 'AT_KEYEXCHANGE')

    @property
    def config(self):
        config = ConfigParser.RawConfigParser()
        config.optionxform = str
        config.read(self.configfile)
        return config

    def __init__(self, name):
        """
        Init hdimage object.

        :name: container name
        """

        self.cont = b'\\\\.\\HDIMAGE\\' + cryptoapi._from_hex(name)
        self.name = name
        self.user = getpass.getuser()
        self.certs = {}

        self.configfile = '/var/opt/cprocsp/users/{0}/local.ini'.format(self.user)
        self.section = r'KeyDevices\passwords\"{0}"'.format(self.name)

        self.broken = False
        self.empty = True
        try:
            self.ctx = csp.Crypt(self.cont, csp.PROV_GOST_2001_DH, csp.CRYPT_SILENT)
        except ValueError:
            try:
                self.ctx = csp.Crypt(
                    self.cont, csp.PROV_GOST_2001_DH, csp.CRYPT_NEWKEYSET | csp.CRYPT_SILENT)
            except:
                self.broken = True
                self.ctx = None
        else:
            try:
                key = self.ctx.get_key()
            except ValueError:
                self.empty = True
            else:
                self.empty = False
                try:
                    cert = key.extract_cert(csp.AT_KEYEXCHANGE)
                    self.certs['AT_KEYEXCHANGE'] = _cert_info(cert)
                except:
                    pass
                try:
                    cert = key.extract_cert(csp.AT_SIGNATURE)
                    self.certs['AT_SIGNATURE'] = _cert_info(cert)
                except:
                    pass

        if not self.broken:
            self.shortcut = self.ctx.uniq_name()
        else:
            if self.config.has_section(self.section):
                self.shortcut = eval(self.config.get(self.section, 'shortcut'))
            else:
                self.shortcut = None
        if self.shortcut:
            self.folder = self.shortcut.split('\\')[2]
            self.dirname = '/var/opt/cprocsp/keys/{0}/{1}'.format(self.user, self.folder)
            self.empty = not os.path.exists(self.dirname)
        else:
            self.folder = self.dirname = None
            self.empty = True

    def initialize(self):
        """
        Setup directory and configuration entry for container

        :returns: None
        """
        if not os.path.isdir(self.dirname):
            os.makedirs(self.dirname)

        cfg = self.config
        if not self.config.has_section(self.section):
            cfg.add_section(self.section)
            cfg.set(self.section, 'shortcut', '"{0}"'.format(self.shortcut.replace('\\', '\\\\')))
            cfg.write(open(self.configfile, 'wt'))

    def backup(self, filename):
        """
        Save key container into archive

        :filename: archive file name
        :arccls: archive management class, compatible with zipfile.ZipFile
        :returns: saved filename
        """

        if not filename:
            filename = self.name.replace('\\', '_') + '.zip'
        with ZipFile(filename, mode='w') as zf:
            if self.ctx and self.dirname:
                for fn in iglob(os.path.join(self.dirname, '*.key')):
                    zf.write(fn, arcname='{0}/{1}'.format(self.folder,
                                                          os.path.basename(fn)))
                for keyname in self._keyspecs:
                    try:
                        keyspec = getattr(csp, keyname)
                        key = self.ctx.get_key(keyspec)
                    except ValueError:
                        continue
                    cert = key.extract_cert()
                    zf.writestr('{0}.cer'.format(keyname), cert)
                zf.close()
        return filename

    def delete(self):
        """
        Remove key container from disk
        """
        if self.empty:
            return
        cfg = self.config
        cfg.remove_section(self.section)
        cfg.write(open(self.configfile, 'wt'))
        shutil.rmtree(self.dirname)
        self.empty = True

    @classmethod
    def check_structure(cls, names):
        """Verify correctness of archive name structure

        :names: name list
        :returns: True/False

        """
        dirs = set(d for d in (_rarsplit(x)[0] for x in names) if d)
        _ensure(len(dirs) == 1, 'One and only one key directory allowed')
        dirname = list(dirs)[0]
        filenames = set(_rarbase(fn) for fn in names
                        if fn.startswith(dirname) and fn.endswith('.key'))
        _ensure(filenames >= cls._names, 'Incomplete file set in archive')
        certs = list(x for x in names
                     if x.endswith('.cer'))
        standard_certs = set(x[:-4] for x in certs
                             if x[:-4] in cls._keyspecs)
        non_standard_certs = set(x for x in certs
                                 if x[:-4] not in cls._keyspecs)
        _ensure(len(non_standard_certs) <= 1,
                'Only one non-standard certificate in archive allowed')
        _ensure((not (non_standard_certs
                      and 'AT_KEYEXCHANGE.cer' in standard_certs)),
                'both AT_KEYEXCHANGE cert and non-standard cert name in archive')
        return dict(dirname=dirname,
                    files=filenames,
                    standard=standard_certs,
                    non_standard=non_standard_certs)

    @classmethod
    def restore(cls, filename, filetype=None, paswd=None, force=False):
        """Create and load container from zip archive contents

        :filename: archive file name
        :filetype: archive type ('rar', 'zip'). Default: autodetect
        :paswd: container PIN
        :returns: new object for container

        """
        ft = filetype or filename.lower()
        if ft.endswith('rar'):
            arccls = RarFile
        elif ft.endswith('zip'):
            arccls = ZipFile
        else:
            _ensure(False, 'Unsupported file type: {0}'.format(ft))

        zf = arccls(filename)
        names = zf.namelist()
        struct = cls.check_structure(names)
        value = zf.read('{0}/name.key'.format(struct['dirname']))
        real_name = bytes(decoder.decode(value)[0][0])
        name = cryptoapi._to_hex(real_name)
        res = cls(name)
        _ensure(res.empty or force, "Container '{0}' exists".format(name))

        if not res.empty or force:
            res.delete()
            del res
        res = cls(name)
        _ensure(res.empty, "Couldn't delete container '{0}'".format(name))
        res.initialize()
        for fn in struct['files']:
            data = zf.read('{0}/{1}'.format(struct['dirname'], fn))
            open(os.path.join(res.dirname, fn), 'wb').write(data)

        del res.ctx
        try:
            res.ctx = csp.Crypt(res.cont, csp.PROV_GOST_2001_DH, csp.CRYPT_SILENT)
            if paswd:
                res.ctx.set_password(str(paswd), csp.AT_KEYEXCHANGE)
                res.ctx.change_password(str(''))
            if struct['non_standard'] or struct['standard']:
                for nsc in struct['non_standard']:
                    certdata = zf.read(nsc)
                    res.certs['AT_KEYEXCHANGE'] = _cert_info(certdata)
                    newc = csp.Cert(certdata)
                    newc.bind(res.ctx, csp.AT_KEYEXCHANGE)
                    cs = csp.CertStore(res.ctx, b"MY")
                    cs.add_cert(newc)
                    key = res.ctx.get_key(csp.AT_KEYEXCHANGE)
                    key.store_cert(newc)
                for nsc in struct['standard']:
                    certdata = zf.read(nsc + '.cer')
                    res.certs[nsc] = _cert_info(certdata)
                    newc = csp.Cert(certdata)
                    keyspec = getattr(csp, nsc)
                    newc.bind(res.ctx, keyspec)
                    cs = csp.CertStore(res.ctx, b"MY")
                    cs.add_cert(newc)
                    key = res.ctx.get_key(keyspec)
                    key.store_cert(newc)
            else:
                for ksp in ('AT_KEYEXCHANGE', 'AT_SIGNATURE'):
                    keyspec = getattr(csp, ksp)
                    try:
                        key = res.ctx.get_key(keyspec)
                        cert = key.extract_cert()
                        res.certs[ksp] = _cert_info(cert)
                        newc = csp.Cert(cert)
                        newc.bind(res.ctx, keyspec)
                        cs = csp.CertStore(res.ctx, b"MY")
                        cs.add_cert(newc)
                    except ValueError:
                        pass

        except:
            cryptoapi.remove_key(res.name)
            raise
        return res

    @classmethod
    def query(cls, filename, filetype=None):
        """Determine container name from archive contents

        :filename: archive file name
        :filetype: archive type ('rar', 'zip'). Default: autodetect
        :returns: container info in dictionary

        """
        res = {}
        ft = filetype or filename.lower()
        if ft.endswith('rar'):
            arccls = RarFile
        elif ft.endswith('zip'):
            arccls = ZipFile
        else:
            _ensure(False, 'Unsupported file type: {0}'.format(ft))

        zf = arccls(filename)
        names = zf.namelist()
        struct = cls.check_structure(names)
        value = zf.read('{0}/name.key'.format(struct['dirname']))
        res['name'] = decoder.decode(value)[0][0]
        res['certs'] = {}

        for nsc in struct['non_standard']:
            certdata = zf.read(nsc)
            res['certs']['AT_KEYEXCHANGE'] = _cert_info(certdata)
        for nsc in struct['standard']:
            certdata = zf.read(nsc + '.cer')
            res['certs'][nsc] = _cert_info(certdata)
        return res
