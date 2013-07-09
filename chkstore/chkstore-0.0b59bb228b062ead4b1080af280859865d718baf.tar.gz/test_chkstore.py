#! /usr/bin/env python

import unittest
import sys
import errno
import os
import shutil
import bz2
from cStringIO import StringIO
import hashlib
import warnings

import chkstore


class TmpDirMixin (object):
    # BUG: This seems like something twisted trial already does.

    def setUp(self):
        cls = type(self)
        self.tmpdir = os.path.join('.', 'testdata', cls.__module__, cls.__name__, self._testMethodName)
        os.makedirs(self.tmpdir)

    def tearDown(self):
        if os.environ.get('TEST_CHKSTORE_SAVE_DIR', 'false') != 'true':
            shutil.rmtree(self.tmpdir)
            path = os.path.dirname(self.tmpdir)
            while path != '.' and not os.listdir(path):
                os.rmdir(path)
                path = os.path.dirname(path)
        else:
            print 'SAVING BACKUP DIRECTORY: {0!r}'.format(self.tmpdir)
        

class CHKStoreTests (TmpDirMixin, unittest.TestCase):

    def setUp(self):
        TmpDirMixin.setUp(self)
        self.storedir = os.path.join(self.tmpdir, 'chkstore')
        chkstore.CHKStore.initialize_storage_directory(self.storedir)
        self.store = chkstore.CHKStore(self.storedir)

    def test_insert(self):
        data = 'There are no facts, only interpretations. -Nietzsche  -especially in automated tests! -nejucomo'
        expectedkey = chkstore.CHK_FUNCTION_PREFIX + hashlib.sha256(data).hexdigest()

        actualkey = self.store.insert_bytes(data)

        self.assertEqual(expectedkey, actualkey)

        actualdata = self.store.read_bytes(actualkey)

        self.assertEqual(data, actualdata)

        actualkeys = list(self.store.iter_keys())

        self.assertEqual([expectedkey], actualkeys)

        st = self.store.content_stat(actualkey)

        # Sort of a dummy test, just ensure stat works:
        self.failUnless(st != None)

    def test_insert_twice(self):
        data = 'foo'
        self.store.insert_bytes(data)
        self.store.insert_bytes(data)

    def test_listkeys_during_insert(self):
        data = 'azbazbaf'
        expectedkey = chkstore.CHK_FUNCTION_PREFIX + hashlib.sha256(data).hexdigest()

        self.store.insert_bytes(data)

        inserter = self.store.open_inserter()

        actualkeys = list(self.store.iter_keys())

        self.assertEqual([expectedkey], actualkeys)

        inserter.close()

        self.assertEqual(2, len(list(self.store.iter_keys())))

    def test_listkeys_with_junk(self):
        with warnings.catch_warnings(record=True) as warningslog:
            with file(os.path.join(self.storedir, 'some_junk'), 'w') as f:
                f.write('Here is some junk in the storage directory.')

            actualkeys = list(self.store.iter_keys())

            self.assertEqual([], actualkeys)
            self.assertEqual(1, len(warningslog))

            [entry] = warningslog
            self.assertEqual(UserWarning, entry.category)
            self.assertEqual('chkstore.py', os.path.basename(entry.filename))

    def test_has_key(self):
        data = "I'd rather have a bottle in front of me than a frontal lobotomy!"
        key = chkstore.CHK_FUNCTION_PREFIX + hashlib.sha256(data).hexdigest()

        self.failIf(self.store.has_key(key))

        self.store.insert_bytes(data)

        self.failUnless(self.store.has_key(key))

    def test_has_key_exception(self):
        data = "I'd rather have a bottle in front of me than a frontal lobotomy!"
        key = self.store.insert_bytes(data)

        os.chmod(self.storedir, 0000) # Remove permissions for stat.
        try:
            try:
                self.store.has_key(key)
            finally:
                os.chmod(self.storedir, 0700) # Restore permissions for stat.
        except os.error, e:
            if e.errno != errno.EACCES:
                # An exception this test did not expect is an error:
                raise
            # Else: the test passes
        else:
            self.fail('has_key masked an unexpected exception.')

    def test_invalid_store_no_schema_file(self):
        invalid = os.path.join(self.tmpdir, 'no_schema_file')
        os.mkdir(invalid)
        with file(os.path.join(invalid, 'somefile'), 'w') as f:
            f.write('This is not a schema file.')
        try:
            chkstore.CHKStore(invalid)
        except chkstore.MalformedStorageDirectory, e:
            expected = '[Errno {0!r}]'.format(errno.ENOENT)
            self.failIf( -1 == e.args[0].find(expected), 'Unexpected error description: {0!s}'.format(e.args[0]))
        else:
            self.fail('CHKStore constructor did not detect missing schema file.')

    def test_invalid_store_garbage_schema(self):
        invalid = os.path.join(self.tmpdir, 'garbage_schema_file')
        os.mkdir(invalid)
        with file(os.path.join(invalid, chkstore.SERIALIZATION_README_NAME), 'w') as f:
            f.write('This is not a schema file.')
        try:
            chkstore.CHKStore(invalid)
        except chkstore.MalformedStorageDirectory:
            pass # Success.
        else:
            self.fail('CHKStore constructor did not detect malformed schema file.')

    def test_invalid_store_unknown_schema_version(self):
        invalid = os.path.join(self.tmpdir, 'future_schema_file')
        os.mkdir(invalid)
        with file(os.path.join(invalid, chkstore.SERIALIZATION_README_NAME), 'w') as f:
            f.write('SERIALIZATION_VERSION: 9120938')
        try:
            chkstore.CHKStore(invalid)
        except chkstore.MalformedStorageDirectory:
            pass # Success.
        else:
            self.fail('CHKStore constructor did not detect unknown schema version.')


class InserterTests (TmpDirMixin, unittest.TestCase):

    def setUp(self):
        TmpDirMixin.setUp(self)
        self.mirror = StringIO()
        self.inserter = chkstore.Inserter(self.tmpdir)

    def test_is_not_tty(self):
        self.assertEqual(False, self.inserter.isatty())
        
    def test_no_op(self):
        self._test_close()
        
    def test_write(self):
        self._write('hello world')
        self._test_close()

    def test_write_invalid_unicode(self):
        self._test_write_invalid_type(u'Unicode is not allowed because the encoding is ambiguous.')

    def test_write_invalid_nonstring(self):
        self._test_write_invalid_type(42)

    def test_writelines(self):
        lines = ['a', 'boof', '\0' * 1024]
        self.mirror.write(''.join(lines))
        self.inserter.writelines(lines)
        self._test_close()

    def test_tell(self):
        data = 'foo ' * 7
        self._write(data)
        expected = len(data)
        self.assertEqual(expected, self.inserter.tell())
        self._test_close()

    def test_unexpected_link_error(self):
        # It's hard to deterministically tweak the filesystem to trigger
        # an error in os.link, so we corrupt the inserter's private state
        # instead:

        # Setting _storagedir to a non-existent directory will lead to
        # keypath in that non-existent directory, causing linking to fail:
        self.inserter._storagedir = "THIS PATH SHOULD NOT EXIST ON ANY SANE SYSTEM.  Have a nice day!"

        try:
            self.inserter.close()
        except os.error, e:
            # If we successfully catch this expected error, the test passes:
            self.assertEqual(errno.ENOENT, e.args[0])

            # Note, any other exception is a test failure, because the test
            # code does not want to mask other unexpected errors.
        else:
            self.fail('Inserter.close did not detect a system error while committing an entry.')

    def _write(self, data):
        self.mirror.write(data)
        self.inserter.write(data)

    def _test_write_invalid_type(self, thing):
        try:
            self.inserter.write(thing)
        except AssertionError:
            pass # The test succeeded.
        else:
            self.fail('The inserter allowed non-bytes to be written: {0!r}'.format(type(thing)))

    def _test_close(self):
        mirrordata = self.mirror.getvalue()

        key = self.inserter.close()
        entrypath = os.path.join(self.tmpdir, key + chkstore.COMPRESSION_SUFFIX)

        self.failUnless(os.path.isfile(entrypath))

        with bz2.BZ2File(entrypath, 'rb') as f:
            actualdata = f.read()

        self.assertEqual(mirrordata, actualdata)

        expectedkey = chkstore.CHK_FUNCTION_PREFIX + hashlib.sha256(mirrordata).hexdigest()

        self.assertEqual(expectedkey, key)

        self.assertEqual(expectedkey, self.inserter.key)
        

class CommandlineToolTests (TmpDirMixin, unittest.TestCase):

    def setUp(self):
        TmpDirMixin.setUp(self)

        self.__outerstdout = sys.stdout
        self.__outerstderr = sys.stderr

        sys.stdout = self.__stdoutbuffer = StringIO()
        sys.stderr = self.__stderrbuffer = StringIO()

        self._storagedir = os.path.join(self.tmpdir, 'chkstore')
        chkstore.DEFAULT_COMMANDLINE_CHK_DIR=self._storagedir

    def tearDown(self):
        TmpDirMixin.tearDown(self)

        sys.stdout = self.__outerstdout
        sys.stderr = self.__outerstderr

    def test_listkeys_with_no_entries(self):
        chkstore.main(['listkeys'])
        self._assert_no_output(self.__stdoutbuffer)
        self._assert_no_output(self.__stderrbuffer)
        
    def test_listkeys_with_two_entries(self):
        # First insert two entries:
        chkstore.CHKStore.initialize_storage_directory(self._storagedir)
        store = chkstore.CHKStore(self._storagedir)

        akey = store.insert_bytes('A')
        bkey = store.insert_bytes('B')

        chkstore.main(['listkeys'])
        self._assert_no_output(self.__stderrbuffer)

        expectedkeys=set([akey, bkey])
        actualkeys=set(self.__stdoutbuffer.getvalue().strip().split('\n'))

        self.assertEqual(expectedkeys, actualkeys)
        
    def test_insert(self):
        data = 'this is yet another input string'
        expectedkey = chkstore.CHK_FUNCTION_PREFIX + hashlib.sha256(data).hexdigest()

        outerstdin = sys.stdin
        sys.stdin = StringIO(data)

        try:
            chkstore.main(['insert'])
        finally:
            sys.stdin = outerstdin

        self._assert_no_output(self.__stderrbuffer)

        actualkey = self.__stdoutbuffer.getvalue().strip()

        self.assertEqual(expectedkey, actualkey)

    def test_read(self):
        data = 'WIGGLE WOOGLE'

        # First insert data:
        chkstore.CHKStore.initialize_storage_directory(self._storagedir)
        store = chkstore.CHKStore(self._storagedir)

        key = store.insert_bytes(data)

        chkstore.main(['read', key])
        self._assert_no_output(self.__stderrbuffer)

        self.assertEqual(data, self.__stdoutbuffer.getvalue())

    # Make sure a pre-existing storage directory succeeds:
    def test_listkeys_with_already_initialized_storagedir(self):
        chkstore.CHKStore.initialize_storage_directory(self._storagedir)
        chkstore.main(['listkeys'])
        self._assert_no_output(self.__stdoutbuffer)
        self._assert_no_output(self.__stderrbuffer)

    # Test usage error cases:
    def test_usage_error_no_command(self):
        self._test_usage_error()

    def test_usage_error_unknown_command(self):
        self._test_usage_error('depl0y_the_bodega')

    def test_usage_error_unexpected_listkeys_arguments(self):
        self._test_usage_error('listkeys', 'this', 'is', 'unexpected')

    def test_usage_error_unexpected_insert_arguments(self):
        self._test_usage_error('insert', 'a', 'fault')

    def test_usage_error_unexpected_read_arguments(self):
        self._test_usage_error('read', 'a', 'tea', 'leaf')

    def test_usage_error_missing_read_arguments(self):
        self._test_usage_error('read')

    # Test malformed storage schema usage errors:
    def test_missing_schema_file(self):
        os.mkdir(self._storagedir)
        try:
            chkstore.main(['listkeys'])
        except SystemExit, e:
            self.failUnless(e.args[0].startswith('Malformed storage directory: '))
            self._assert_no_output(self.__stdoutbuffer)
            self._assert_no_output(self.__stderrbuffer)
        else:
            self.fail('Expected MalformedStorageDirectory error but it was not raised.')

    # Test unusual filesystem exceptions:
    def test_ioerror_while_initializing_chkstore_raises_exception(self):
        try:
            chkstore.main(['--chk-dir', '/THIS_SHOULD_CAUSE_A_PERMISSIONS_ERROR', 'listkeys'])
        except os.error, e:
            self.assertEqual(errno.EACCES, e.errno)
        else:
            self.fail('main swallowed an unexpected filesystem exception.')

    # Private:
    def _test_usage_error(self, *args):
        try:
            chkstore.main(list(args))
        except SystemExit, e:
            # BUG: Magic constant 2 is what optparse seems to use:
            self.assertEqual(2, e.args[0])
            self._assert_no_output(self.__stdoutbuffer)
            self.failUnless(self.__stderrbuffer.getvalue().startswith('Usage:'))
        else:
            self.fail('Expected usage error not raised.')

    def _assert_no_output(self, buffer):
        self.assertEqual('', buffer.getvalue())


if __name__ == '__main__':
    unittest.main()
