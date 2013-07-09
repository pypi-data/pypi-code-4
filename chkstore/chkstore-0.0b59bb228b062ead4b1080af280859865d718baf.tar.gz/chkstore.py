#! /usr/bin/env python
"""
A library for multi-process-safe Content-Hash-Keyed local file storage.
"""
import os
import errno
import hashlib
import bz2
import warnings

# For commandline tool:
import sys
import optparse


SERIALIZATION_VERSION = 0
CHK_FUNCTION_PREFIX = 'sha256_'
COMPRESSION_SUFFIX = '.bz2'


# The README begins with '_' so that it sorts last compared to the
# other entry types.  Thus if a data archaelogist runs "ls" in a large
# storage directory, they are more likely to see the _README_ at the end
# of the output:
SERIALIZATION_README_NAME = '_README_'

SERIALIZATION_README_CONTENTS = """\
SERIALIZATION_VERSION: {VERSION!r}

This directory is a Content-Hash-Keyed storage directory, as created by
the chkstore tool or a program which uses that library.  That tool
currently lives at:

https://bitbucket.org/nejucomo/chkstore

Content-Hash-Keyed means the lookup key is based on some deterministic
function of the contents.  Ideally this function has the properties of
a cryptographic hash function.  In this directory, the key function is
the SHA256 hash function.

The file names of completely inserted entries contain this key so that
indexing is performed mostly by the filesystem (see below).

The files ending with {SUFFIX!s} are compressed with the bz2 algorithm.

Each entry in this directory is one of three formats:

{README_NAME!s}
  This file, which must begin with a serialization version specifier on
  the first line.

incoming_<hex digits>.{SUFFIX!s}
  A pending insert into the storage directory.  This stores incoming
  data on the filesystem before its key is known.  The hex digits are
  chosen at random to prevent two different inserts from writing to the
  same file accidentally.

{PREFIX!s}<hex digits>{SUFFIX!s}
  A completely inserted entry. The prefix "{PREFIX!s}" identifies the
  hash function used.  The hash is over the *uncompressed* contents.
  Compression is merely to save disk space and is not part of the CHK
  interface.

Any other file is "junk" and the chkstore library will issue warnings
when it notices junk files.

""".format(VERSION = SERIALIZATION_VERSION,
           README_NAME = SERIALIZATION_README_NAME,
           PREFIX = CHK_FUNCTION_PREFIX,
           SUFFIX = COMPRESSION_SUFFIX)


DEFAULT_COMMANDLINE_CHK_DIR=os.path.expanduser('~/.chkstore')


def main(args = sys.argv[1:]):
    """
    Usage: %prog [options] COMMAND ARGS...

    Commands:

      %prog listkeys
        Print a list of all keys to stdout, one per line.

      %prog insert
        Insert stdin into the store. Print the key on stdout.

      %prog read KEY
        Print the contents of key to stdout.
    """
    p = optparse.OptionParser(usage=main.__doc__)
    p.allow_interspersed_args = False
    p.add_option('--chk-dir',
                 type='str',
                 dest='chkdir',
                 default=DEFAULT_COMMANDLINE_CHK_DIR,
                 help='The CHKStore path.')

    opts, args = p.parse_args(args)

    if len(args) == 0:
        p.error('No COMMAND specified.')

    try:
        CHKStore.initialize_storage_directory(opts.chkdir)
    except os.error, e:
        if e.errno != errno.EEXIST:
            raise

    command, cmdargs = args[0], args[1:]

    bufsize = 2 ** 16
    try:
        store = CHKStore(opts.chkdir)
    except MalformedStorageDirectory, e:
        raise SystemExit('Malformed storage directory: {0!s}'.format(e.args[0]))

    if command == 'listkeys':
        if len(cmdargs) != 0:
            p.error('Unexpected arguments to listkeys command: {0!r}'.format(cmdargs))
        for key in store.iter_keys():
            sys.stdout.write(key + '\n')
    elif command == 'insert':
        if len(cmdargs) != 0:
            p.error('Unexpected arguments to insert command: {0!r}'.format(cmdargs))
        inserter = store.open_inserter()
        buf = sys.stdin.read(bufsize)
        while buf:
            inserter.write(buf)
            buf = sys.stdin.read(bufsize)
        key = inserter.close()
        print key
    elif command == 'read':
        try:
            [key] = cmdargs
        except ValueError:
            p.error('Wrong number of arguments to read command: {0!r}'.format(cmdargs))
        reader = store.open_reader(key)
        buf = reader.read(bufsize)
        while buf:
            sys.stdout.write(buf)
            buf = reader.read(bufsize)
    else:
        p.error('Unknown command: {0!r}'.format(command))



class MalformedStorageDirectory (Exception): pass


class CHKStore (object):

    @staticmethod
    def is_key_shaped(s):
        return type(s) is str and s.startswith(CHK_FUNCTION_PREFIX) and len(s) == CHKStore._KEY_LENGTH

    @staticmethod
    def initialize_storage_directory(path):
        """Create a new chkstore directory."""
        os.mkdir(path)
        with file(os.path.join(path, SERIALIZATION_README_NAME), 'w') as f:
            f.write(SERIALIZATION_README_CONTENTS)

    def __init__(self, storagedir):
        """
        The storagedir must have been previously initialized by
        CHKStore.initialize_storage_directory.
        """
        self._validate_schema(storagedir)
        self._storagedir = storagedir

    # Simple bytes API for small entries:
    def insert_bytes(self, data):
        f = self.open_inserter()
        f.write(data)
        return f.close()

    def read_bytes(self, key):
        with self.open_reader(key) as f:
            return f.read()

    # File-oriented API for arbitrarily large entries:
    def open_inserter(self):
        """
        Return a new Inserter for this CHKStore.
        """
        return Inserter(self._storagedir)

    def open_reader(self, key):
        """
        Return a readable file handle for the given key or raise an
        IOError if it does not exist.
        """
        return bz2.BZ2File(self._key_path(key), 'rb')

    # Index-related API:
    def iter_keys(self):
        """
        Generate a sequence of stored keys.
        """
        for path in os.listdir(self._storagedir):
            if path == SERIALIZATION_README_NAME or path.startswith(Inserter.IncomingPrefix):
                continue

            elif path.endswith(COMPRESSION_SUFFIX) and CHKStore.is_key_shaped(path[:-len(COMPRESSION_SUFFIX)]):
                key = path[:-len(COMPRESSION_SUFFIX)]
                yield key

            else:
                warnings.warn('Junk in storage directory: {0!r}'.format(path))

    def has_key(self, key):
        try:
            self.content_stat(key)
        except os.error, e:
            if e.errno != errno.ENOENT:
                raise
            else:
                return False
        else:
            return True
 
    def content_stat(self, key):
        return os.stat(self._key_path(key))


    # Private:
    _KEY_LENGTH = len(CHK_FUNCTION_PREFIX) + (hashlib.sha256().digestsize * 2) # * 2 for hex encoding.

    @staticmethod
    def _validate_schema(storagedir):
        schemapath = os.path.join(storagedir, SERIALIZATION_README_NAME)

        try:
            with file(schemapath, 'r') as f:
                try:
                    [header, versionText] = f.readline().strip().split(':', 1)
                    version = int(versionText)
                except (ValueError, TypeError):
                    header = None
        except IOError, e:
            raise MalformedStorageDirectory(str(e))

        if header != 'SERIALIZATION_VERSION':
            raise MalformedStorageDirectory('Schema file {0!r} does not have a valid version line.'.format(schemapath))
        elif version != SERIALIZATION_VERSION:
            raise MalformedStorageDirectory('Unsupported schema version: {0!r}'.format(version))

    def _key_path(self, key):
        return _key_path(self._storagedir, key)


class Inserter (object):
    """
    An Inserter is a writable-file-like object which adds the written
    contents to a CHKStore on close.
    """
    IncomingPrefix = 'incoming_'

    def __init__(self, storagedir):
        self._hasher = hashlib.sha256()
        self._storagedir = storagedir

        tmppath = _key_path(storagedir, self.IncomingPrefix + os.urandom(16).encode('hex'))

        fd = os.open(tmppath, os.O_CREAT | os.O_EXCL, 0600)

        self._spool = bz2.BZ2File(tmppath, 'wb')

        os.close(fd)

        self._key = None

    @property
    def closed(self):
        return self._key is not None

    @property
    def key(self):
        assert self.closed
        return self._key

    def close(self):
        key = CHK_FUNCTION_PREFIX + self._hasher.hexdigest()

        destpath = _key_path(self._storagedir, key)

        # BUG: destpath may already exist.
        try:
            os.link(self._spool.name, destpath)
        except os.error, e:
            if e.errno != errno.EEXIST:
                raise

        self._spool.close() # Unlinks the spool file.

        os.remove(self._spool.name)

        os.chmod(destpath, 0400)

        self._key = key

        return self.key

    def isatty(self):
        return False

    def tell(self):
        return self._spool.tell()

    def write(self, data):
        try:
            assert type(data) is bytes, 'Only bytes may be written into a chkstore, not {0!r}'.format(type(data))
            self._spool.write(data)
            self._hasher.update(data)
        except:
            # Clean up:
            self._spool.close()
            os.unlink(self._spool.name) # Warning: An exception would mask the original problem.
            self._spool = self._hasher = None
            raise

    def writelines(self, lines):
        for data in lines:
            self.write(data)


def _key_path(basedir, key):
    return os.path.join(basedir, key + COMPRESSION_SUFFIX)


if __name__ == '__main__':
    main()
