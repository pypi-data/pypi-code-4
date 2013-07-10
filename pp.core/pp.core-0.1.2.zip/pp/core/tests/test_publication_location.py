# -*- coding=utf-8 *-*

################################################################
# pp.core - Produce & Publish
# (C) 2013, ZOPYX Limited, www.zopyx.com
################################################################

import os
import shutil
import unittest
import tempfile
import fs_base

from pp.core.project import PublishingLocation

class Base(object):

    def _populate_current(self):
        for i in range(5):
            destname = os.path.join(self.project.current_path, 'name%d' % i)
            with self.fslayer.open(destname, 'w') as fp:
                fp.write('hello world')

    def test_create_structure(self):
        assert self.project.fslayer.exists(self.project.current_path) == True
        assert self.project.fslayer.exists(self.project.archive_path) == True
        assert self.project.all_archived_versions() == []

    def test_listdir(self):
        self._populate_current()
        assert len(self.fslayer.listdir(self.project.current_path)) == 5

    def test_clear_directory(self):
        self._populate_current()
        self.project.clear_directory(self.project.current_path)
        assert len(self.fslayer.listdir(self.project.current_path)) == 0

    def test_copy_from_localfs(self):
        src = os.path.join(os.path.dirname(__file__), 'sampledata')
        self.project.copy_from_localfs(src, 'target_directory')
        assert len(self.project.fslayer.listdir('target_directory')) == 3


class LocalFSTests(fs_base.LocalFSTests, Base):
    factory = PublishingLocation

class S3FSTests(fs_base.S3FSTests, Base):
    factory = PublishingLocation

class SFTPFSTests(fs_base.SFTPFSTests, Base):
    factory = PublishingLocation

class DropboxFSTests(fs_base.DropboxFSTests, Base):
    factory = PublishingLocation
