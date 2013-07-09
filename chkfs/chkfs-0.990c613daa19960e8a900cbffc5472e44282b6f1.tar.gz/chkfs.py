#! /usr/bin/env python

import os
import stat
import time
import errno
import pwd
import grp
import sys
import argparse
import logging
import inspect

from chkstore import CHKStore
from jsonchkstore import JsonCHKStore


DESCRIPTION = """\
Create/Restore backup snapshots of a file system using a chkstore system
for deduplication and backup-host filesystem independence.
"""

STORAGE_ENV_NAME = 'CHKFS_STORAGE'

STAT_FIELDS = ['atime', 'ctime', 'gid', 'mode', 'mtime', 'size', 'uid']
# NOTE: We *ignore* blksize, blocks, dev, ino, nlink, rdev

STAT_MODE_TYPE_NAMES = ['BLK', 'CHR', 'DIR', 'FIFO', 'LNK', 'REG', 'SOCK']

TIME_FORMAT = '%Y-%m-%dT%H:%M:%S%z'

BUFSIZE = 2**16



def main(args = sys.argv[1:]):
    cmdline = Commandline(args)
    cmdline.run()


class Commandline (object):
    def __init__(self, args):
        self.cmdargs = []

        p = argparse.ArgumentParser(description=DESCRIPTION)

        p.add_argument('--log-level',
                       dest='loglevel',
                       default='INFO',
                       choices=['DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL'],
                       help='Set logging level.')

        p.add_argument('--storage',
                       type=str,
                       dest='storage',
                       default=os.environ.get(STORAGE_ENV_NAME),
                       help='The directory for backup storage.')

        subp = p.add_subparsers(title='Operations')

        for attr in dir(self):
            if attr.startswith('cmd_'):
                self._add_command_options(subp, attr[4:], getattr(self, attr))

        p.parse_args(args, self)

        if self.storage is None:
            p.error(
                'Either the %r environment variable must be set or --storage must be passed.' % (
                    STORAGE_ENV_NAME,
                    )
                )

        logging.basicConfig(
            stream=sys.stdout,
            format='%(asctime)s %(levelname) 5s %(name)s | %(message)s',
            datefmt=TIME_FORMAT,
            level=getattr(logging, self.loglevel))

    def cmd_init(self):
        """Initialize STORAGE as a chkfs storage directory."""
        CHKFS.initialize_chkfs_storage(self.storage)

    def cmd_backup(self, PATH, *PATHS):
        """Make a snapshot backup of PATHS."""
        paths = [PATH] + list(PATHS)

        chkfs = CHKFS(self.storage)
        chkfs.create_backup(paths)

    # Private:
    def _add_command_options(self, subp, name, method):
        parser = subp.add_parser(name, help=method.__doc__)

        parser.set_defaults(run = lambda : method(*self.cmdargs))

        (argnames, varargs, keywords, defaults) = inspect.getargspec(method)

        assert (keywords, defaults) == (None, None), \
            'cmd method interface violation: %r' % (method,)
        assert argnames[:1] == ['self'], \
            'cmd method interface violation: %r' % (method,)

        for argname in argnames[1:]:
            parser.add_argument(argname,
                                action=AppendArgs)

        if varargs is not None:
            parser.add_argument(varargs,
                                action=AppendArgs,
                                nargs = '*')


class CHKFS (object):

    @staticmethod
    def initialize_chkfs_storage(storagedir, logger=None):
        if logger is None:
            logger = logging.getLogger('CHKFS-init')

        logger.debug('Creating %r', storagedir)
        os.mkdir(storagedir)
        for path in CHKFS._get_chkpaths(storagedir):
            logger.debug('Initializing chkstore %r', path)
            CHKStore.initialize_storage_directory(path)

    def __init__(self, storagedir):
        [blobpath, snapshotpath, dirnodepath] = CHKFS._get_chkpaths(storagedir)

        self._log = logging.getLogger(type(self).__name__)
        self._blobstore = CHKStore(blobpath)
        self._snapshotstore = JsonCHKStore(snapshotpath)
        self._dirnodestore = JsonCHKStore(dirnodepath)
        self._mounts = self._init_mount_table()

    def create_backup(self, paths):
        paths = [ os.path.abspath(p) for p in paths ]

        self._log.info('Running backup: %r', paths)

        snapshotkey = self._snapshotstore.insert_json(
            dict(
                completed = time.strftime(TIME_FORMAT),
                mount = self._mounts,
                mapping = self._backup_directory_entries(
                    (p, p) for p in paths
                    ),
                )
            )
        self._log.info('Snapshot key: %r', snapshotkey)
        return snapshotkey

    # Private
    @staticmethod
    def _get_chkpaths(storagedir):
        return [ os.path.join(storagedir, p) for p in ['blob', 'snapshots', 'dirnodes'] ]

    def _direntry_backup(self, path):
        """Returns a directory edge structure."""
        info = PathInfo(path)
        self._log.debug('Backing up: %r', info)

        return dict(
            stat = info.jsonstat,
            mountinfo = info.jsonmountinfo,
            data = self._backup_fileinfo_data(info),
            )

    def _backup_fileinfo_data(self, info):
        if info.issymlink:
            return dict(
                type = 'symlink',
                target = info.symlinktarget,
                )
        elif info.isfile:
            return dict(
                type = 'file',
                blobref = self._backup_file_body(info),
                )
        elif info.isdir:
            return dict(
                type = 'directory',
                jsonref = self._backup_directory_fileinfo(info),
                )
        else:
            return dict(type = 'other')

    def _backup_file_body(self, info):
        """Returns a contentkey."""
        self._log.debug('Inserting regular file: %r', info)
        inserter = self._blobstore.open_inserter()
        with file(info.path, 'rb') as rf:
            buf = rf.read(BUFSIZE)
            while buf:
                inserter.write(buf)
                buf = rf.read(BUFSIZE)
        return inserter.close()

    def _backup_directory_fileinfo(self, info):
        """Returns a contentkey."""
        return self._backup_directory_entries(
            (n, os.path.join(info.path, n))
            for n in os.listdir(info.path)
            )

    def _backup_directory_entries(self, mapping):
        """mapping - iter over ( name, path ). Returns a contentkey."""
        return self._dirnodestore.insert_json(
            dict(
                (k, self._direntry_backup(v))
                for (k, v) in mapping
                )
            )

    @classmethod
    def _init_mount_table(cls):
        mounts = {} # Follows the schema for snapshot["mount"].
        uuids = cls._init_dev_metadata_table('uuid')
        labels = cls._init_dev_metadata_table('id')

        with file('/proc/mounts', 'rt') as f:
            for line in f.readlines():
                [device, mountpath, fstype, flags, _, _] = line.split()
                mountinfos = mounts.setdefault(mountpath, [])
                mountinfos.append(
                    dict(
                        device = device,
                        fstype = fstype,
                        mountopts = flags,
                        uuid = uuids.get(device),
                        label = labels.get(device),
                        )
                    )

        return mounts

    @staticmethod
    def _init_dev_metadata_table(metadataname):
        linkdir = '/dev/disk/by-' + metadataname
        table = {} # { devpath -> metadata }

        for metadata in os.listdir(linkdir):
            dev = os.readlink(os.path.join(linkdir, metadata))
            table[dev] = metadata

        return table


class PathInfo (object):
    # BUG: Handle filename encodings.

    def __init__(self, path):
        self._path = os.path.abspath(path)

        st = os.lstat(path)

        self._jsonstat = dict( (field, getattr(st, 'st_' + field)) for field in STAT_FIELDS )
        self._stmode = st.st_mode
        self._typename = self._st_mode_to_type_name(st.st_mode)
        self._uname = self._get_mounted_username(st.st_uid)
        self._gname = self._get_mounted_groupname(st.st_gid)

        self._symlinktarget = None
        if self.issymlink:
            self._symlinktarget = os.readlink(path)

    def __repr__(self):
        return '<PathInfo %(_path)r %(_typename)s m:%(_stmode)05o u:%(_uname)s g:%(_gname)s>' % vars(self)

    @property
    def path(self):
        return self._path

    @property
    def jsonstat(self):
        return self._jsonstat

    @property
    def jsonmountinfo(self):
        return {'username': self._uname, 'groupname': self._gname}

    @property
    def typename(self):
        return self._typename

    @property
    def issymlink(self):
        return stat.S_ISLNK(self._stmode)

    @property
    def isfile(self):
        return stat.S_ISREG(self._stmode)

    @property
    def isdir(self):
        return stat.S_ISDIR(self._stmode)

    @property
    def symlinktarget(self):
        return self._symlinktarget

    # Private:
    @staticmethod
    def _st_mode_to_type_name(mode):
        for name in STAT_MODE_TYPE_NAMES:
            macro = getattr(stat, 'S_IS' + name)
            assert callable(macro), `mode, name, macro`
            if macro(mode):
                return name
        return 'UNKNOWN_MODE_{0!r}'.format(mode)

    @staticmethod
    def _get_mounted_username(uid):
        try:
            return pwd.getpwuid(uid).pw_name
        except KeyError:
            return None

    @staticmethod
    def _get_mounted_groupname(gid):
        try:
            return grp.getgrgid(gid).gr_name
        except KeyError:
            return None


def _ensure_dir_exists(path):
    try:
        os.mkdir(path)
    except os.error, e:
        if e.errno != errno.EEXIST:
            raise


class AppendArgs (argparse.Action):
    """An argument parsing helper."""
    def __call__(self, _parser, namespace, value, _optstr):
        if type(value) is list:
            namespace.cmdargs.extend(value)
        else:
            namespace.cmdargs.append(value)



if __name__ == '__main__':
    main()
