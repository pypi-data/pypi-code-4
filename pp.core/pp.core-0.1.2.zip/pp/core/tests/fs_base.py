# -*- coding=utf-8 -*-

################################################################
# pp.core - Produce & Publish
# (C) 2013, ZOPYX Limited, www.zopyx.com
################################################################

import os
import tempfile
import shutil 
import unittest

from pp.core.fslayer import Filesystems

def get_fslayer(name):
    configuration_filename = os.environ.get('PPCORE_CONFIG')
    if not configuration_filename:
        raise ValueError('pp.core configuration file {} does not existing'.format(configuration_filename))
    fslayer = Filesystems(configuration_filename)
    return fslayer[name]


class LocalFSTests(unittest.TestCase):

    factory = None
    def setUp(self):
        self.fslayer = get_fslayer('localfs')
        self.project = self.factory(u'Mein schönes Projekt', self.fslayer, create=True)

    def tearDown(self):
        shutil.rmtree(self.fslayer.root_path)


class S3FSTests(unittest.TestCase):
    factory = None

    def setUp(self):
        self.fslayer = get_fslayer('aws')
        self.project = self.factory(u'Mein schönes Projekt', self.fslayer, create=True)

    def tearDown(self):
        bucket = self.fslayer._tlocal.s3bukt[0]
        rs = bucket.get_all_keys()
        for key in rs:
            bucket.delete_key(key)
        self.fslayer._tlocal.s3conn[0].delete_bucket(self.fslayer._bucket_name) 


class SFTPFSTests(unittest.TestCase):
    factory = None

    def setUp(self):
        self.fslayer = get_fslayer('sftpfs')
        self.project = self.factory(u'Mein schönes Projekt', self.fslayer, create=True)

    def tearDown(self):

        fslayer = self.project.fslayer
        names = [n for n in fslayer.walkfiles()]
        names.sort(lambda x,y: -cmp(x.count('/'), y.count('/')))
        for name in names:
            fslayer.remove(name)
        names = [n for n in fslayer.walkdirs()]
        names.sort(lambda x,y: -cmp(x.count('/'), y.count('/')))
        for name in names:
            fslayer.removedir(name)


class DropboxFSTests(unittest.TestCase):
    factory = None

    def setUp(self):
        self.fslayer = get_fslayer('dropbox')
        self._cleanup()
        self.project = self.factory(u'Mein schönes Projekt', self.fslayer, create=True)

    def tearDown(self):
        """ Cleanup and house-keeping """
        self._cleanup()

    def _cleanup(self):
        fslayer = self.fslayer
        for name in fslayer.listdir():
            if fslayer.isfile(name):
                fslayer.remote(name)
            elif fslayer.isdir(name):
                fslayer.removedir(name, recursive=True, force=True)
