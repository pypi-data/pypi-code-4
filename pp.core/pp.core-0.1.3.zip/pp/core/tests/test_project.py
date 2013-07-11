# -*- coding=utf-8 *-*

################################################################
# pp.core - Produce & Publish
# (C) 2013, ZOPYX Limited, www.zopyx.com
################################################################

import os
import shutil
import unittest
import tempfile
from pp.core.project import Project
import fs_base

class Base(object):

    def _populate_current(self):
        for i in range(5):
            destname = os.path.join(self.project.current_path, 'name%d' % i)
            with self.fslayer.open(destname, 'w') as fp:
                fp.write('hello world')

    def test_create_structure(self):
        assert self.project.fslayer.exists(self.project.current_path) == True
        assert self.project.fslayer.exists(self.project.drafts_path) == True
        assert self.project.fslayer.exists(self.project.versions_path) == True
        assert self.project.all_versions() == []
        assert self.project.all_drafts() == []

    def test_listdir(self):
        self._populate_current()
        assert len(self.fslayer.listdir(self.project.current_path)) == 5

    def test_clear_directory(self):
        self._populate_current()
        self.project.clear_directory(self.project.current_path)
        assert len(self.fslayer.listdir(self.project.current_path)) == 0

    def test_create_version(self):
        self._populate_current()
        assert self.project.all_versions() == []
        new_version = self.project.create_version()
        new_version_path = os.path.join(self.project.versions_path, new_version)
        assert new_version_path.endswith('V-1') == True
        assert len(self.fslayer.listdir(new_version_path)) == 5
        assert len(self.project.all_versions()) == 1

    def test_copy_from_localfs(self):
        src = os.path.join(os.path.dirname(__file__), 'sampledata')
        self.project.copy_from_localfs(src, 'target_directory')
        assert len(self.project.fslayer.listdir('target_directory')) == 3

    def test_create_demo_content(self):
        self.project.create_demo_content()


class LocalFSTests(fs_base.LocalFSTests, Base):
    factory = Project

class S3FSTests(fs_base.S3FSTests, Base):
    factory = Project

class SFTPFSTests(fs_base.SFTPFSTests, Base):
    factory = Project

class DropboxFSTests(fs_base.DropboxFSTests, Base):
    factory = Project
