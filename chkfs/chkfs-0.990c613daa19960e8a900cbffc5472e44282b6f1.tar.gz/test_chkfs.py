#! /usr/bin/env python

import unittest
import os
import sys
import errno
import stat
import hashlib
import subprocess
import logging

from test_chkstore import TmpDirMixin
import chkstore

import chkfs


STORAGE_SIZE_HIGH_WATERMARK = 70


class LoggingTmpDirMixin (TmpDirMixin):
    def setUp(self):
        TmpDirMixin.setUp(self)
        logging.basicConfig(
            filename=os.path.join(self.tmpdir, 'log'),
            format='%(asctime)s %(levelname) 5s %(name)s | %(message)s',
            datefmt='%Y-%m-%dT%H:%M:%S%z',
            level=logging.DEBUG)


class CommandlinePreInitTest (LoggingTmpDirMixin, unittest.TestCase):
    def test_init(self):
        chkfs.main(['--storage', os.path.join(self.tmpdir, 'storage'), 'init'])

    def test_missing_storage(self):
        with StderrSwallower():
            with self.assertRaises(SystemExit):
                chkfs.main(['init'])

    def test_missing_command(self):
        with StderrSwallower():
            with self.assertRaises(SystemExit):
                chkfs.main([])

    def test_invalid_command(self):
        with StderrSwallower():
            with self.assertRaises(SystemExit):
                chkfs.main(['fnoop'])


class InputDirectoryMixin (LoggingTmpDirMixin):
    def setUp(self):
        LoggingTmpDirMixin.setUp(self)

        def _make_fs(path, value):
            if type(value) is dict:
                os.mkdir(path)
                for (name, value) in value.iteritems():
                    _make_fs(os.path.join(path, name), value)
            elif type(value) is str:
                with file(path, 'wb') as f:
                    f.write(value)
            elif callable(value):
                value(path)
            else:
                raise NotImplementedError((path, value))

        self._storagedir = os.path.join(self.tmpdir, 'storage')
        self._inputdir = os.path.join(self.tmpdir, 'input')

        dupdir = dict(
            a = 'some file contents',
            b = 'some more file contents',
            blink = lambda p: os.symlink('./b', p),
            dangling = lambda p: os.symlink('non_existent_target', p),
            )

        self._inputcontent = {
            'README': 'Foo!',
            'd1': dupdir,
            'd2': dupdir,
            'devicefile': os.mkfifo,
            }

        _make_fs(self._inputdir, self._inputcontent)

    def _check_leaves(self):
        def _check_leaf(node):
            if isinstance(node, str):
                key = chkstore.CHK_FUNCTION_PREFIX + hashlib.sha256(node).hexdigest() + chkstore.COMPRESSION_SUFFIX
                expectedpath = os.path.join(self._storagedir, 'blob', key)
                self.failUnless(
                    os.path.isfile(expectedpath),
                    'Expected leaf file %r with contents %r' % (
                        expectedpath,
                        node,
                        )
                    )
            elif callable(node):
                pass # Ignore special files.
            else:
                for child in node.itervalues():
                    _check_leaf(child)

        _check_leaf(self._inputcontent)

        # Finally check the total space usage here; we want to notice
        # space usage regressions:
        size = int(subprocess.check_output(['du', '-sk', self._storagedir]).split()[0])
        print '\nSize of storage (KiB): %d' % (size,)
        assert size <= STORAGE_SIZE_HIGH_WATERMARK, `size, STORAGE_SIZE_HIGH_WATERMARK`


class CommandlineTests (InputDirectoryMixin, unittest.TestCase):
    def setUp(self):
        InputDirectoryMixin.setUp(self)
        self._run_main('init')

    def test_stats(self):
        self._run_main('backup', self._inputdir)

    # Private:
    def _run_main(self, *args):
        chkfs.main(['--storage', self._storagedir] + list(args))


class CHKFSTests (InputDirectoryMixin, unittest.TestCase):

    def setUp(self):
        InputDirectoryMixin.setUp(self)

        chkfs.CHKFS.initialize_chkfs_storage(self._storagedir)
        self.chkfs = chkfs.CHKFS(self._storagedir)

    def test_backup_and_examine_leaves(self):
        self.chkfs.create_backup([self._inputdir])
        self._check_leaves()

    def test_subsequent_backups(self):
        def walk_path(path, pathset):
            pathset.add(path)
            if os.path.isdir(path):
                for n in os.listdir(path):
                    walk_path(os.path.join(path, n), pathset)
            return pathset

        self.chkfs.create_backup([self._inputdir])
        first = walk_path(self._storagedir, set())

        self.chkfs.create_backup([self._inputdir])
        second = walk_path(self._storagedir, set())

        desc = repr({'first':first, 'second':second})
        self.assertGreaterEqual(2, len(second - first), desc)
        self.assertEqual(set(), first - second, desc)


class PathInfoTests (unittest.TestCase):
    # BUG: These tests may be too platform-specific by depending on /,
    # fs-specific modes, and pwd/grp dbs..

    def test_root_pathinfo_attributes(self):
        info = chkfs.PathInfo('/')
        self.assertEqual('/', info.path)
        self.assertEqual('DIR', info.typename)
        self.assertEqual(False, info.issymlink)
        self.assertEqual(False, info.isfile)
        self.assertEqual(True, info.isdir)

    def test_pathinfo_repr(self):
        info = chkfs.PathInfo('/')
        self.assertEqual("<PathInfo '/' DIR m:40755 u:root g:root>", repr(info))

    # Private utility function tests:
    def test_st_mode_to_type_name(self):
        testvector = [
            ('BLK', stat.S_IFBLK),
            ('CHR', stat.S_IFCHR),
            ('DIR', stat.S_IFDIR),
            ('FIFO', stat.S_IFIFO),
            ('LNK', stat.S_IFLNK),
            ('REG', stat.S_IFREG),
            ('SOCK', stat.S_IFSOCK),
            ('UNKNOWN_MODE_0', 0)]

        for expected, input in testvector:
            assert type(input) is int, `expected, input`
            self.assertEqual(expected, chkfs.PathInfo._st_mode_to_type_name(input))

    def test_get_mounted_username_for_root(self):
        self.assertEqual('root', chkfs.PathInfo._get_mounted_username(0))

    def test_get_mounted_username_for_nonexistent(self):
        # BUG: There's a chance this uid is valid.
        self.assertEqual(None, chkfs.PathInfo._get_mounted_username(2**15-7))

    def test_get_mounted_groupname_for_root(self):
        self.assertEqual('root', chkfs.PathInfo._get_mounted_groupname(0))

    def test_get_mounted_groupname_for_nonexistent(self):
        # BUG: There's a chance this gid is valid.
        self.assertEqual(None, chkfs.PathInfo._get_mounted_groupname(2**15-7))


class UtilFunctionTests (TmpDirMixin, unittest.TestCase):
    def setUp(self):
        TmpDirMixin.setUp(self)
        self.targetdir = os.path.join(self.tmpdir, 'a_directory')

    def test_ensure_directory_exists_on_new_dir(self):
        chkfs._ensure_dir_exists(self.targetdir)
        self.failUnless(os.path.isdir(self.targetdir))

    def test_ensure_directory_exists_on_existing_dir(self):
        os.mkdir(self.targetdir)
        self.test_ensure_directory_exists_on_new_dir()

    def test_ensure_directory_exists_does_not_swallow_exceptions(self):
        os.chmod(self.tmpdir, 0) # Remove write permission in the parent directory.
        try:
            try:
                chkfs._ensure_dir_exists(self.targetdir)
            except os.error, e:
                if e.errno != errno.EACCES:
                    raise # Unexpected exceptions are a test error.
                # Else: The test passes because the exception was not swallowed.
            else:
                self.fail('chkfs._ensure_dir_exists swallowed a permissions exception.')
        finally:
            os.chmod(self.tmpdir, 0700) # Restore write permission for cleanup.


class StderrSwallower (object):
    def __enter__(self):
        self._stderr = sys.stderr
        sys.stderr = open('/dev/null', 'w')

    def __exit__(self, *a):
        sys.stderr.close()
        sys.stderr = self._stderr



if __name__ == '__main__':
    unittest.main()
