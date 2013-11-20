# Copyright 2013 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

"""Python interface to ``liblockfile``."""

from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
    )

__metaclass__ = type
__all__ = [
    "Lock",
    "LockHolder",
    "LockingError",
    "MandatoryLockError",
    "MaxAttemptsError",
    "NameTooLongError",
    "TempLockError",
    "TempLockWriteError",
    "UnknownError",
]

import ctypes
import ctypes.util
import os
import sys
import threading

#define L_SUCCESS       0       /* Lockfile created                     */
L_SUCCESS = 0
#define L_NAMELEN       1       /* Recipient name too long              */
L_NAMELEN = 1
#define L_TMPLOCK       2       /* Error creating tmp lockfile          */
L_TMPLOCK = 2
#define L_TMPWRITE      3       /* Can't write pid int tmp lockfile     */
L_TMPWRITE = 3
#define L_MAXTRYS       4       /* Failed after max. number of attempts */
L_MAXTRYS = 4
#define L_ERROR         5       /* Unknown error; check errno           */
L_ERROR = 5
#define L_MANLOCK       6       /* Cannot set mandatory lock on tempfile */
L_MANLOCK = 6

#define L_PID           16      /* Put PID in lockfile                  */
L_PID = 16
#define L_PPID          32      /* Put PPID in lockfile                 */
L_PPID = 32


liblockfile_filename = ctypes.util.find_library("lockfile")
liblockfile = ctypes.CDLL(liblockfile_filename, use_errno=True)


class LockingError(Exception):
    """Base class for all locking errors."""

    code = None

    def __repr__(self):
        return self.__str__()

    # Python 2
    if sys.version_info.major == 2:

        def __unicode__(self):
            return "[Error %d] %s; called with %r" % (
                self.code, self.__doc__.rstrip("."), self.args)

        def __str__(self):
            return self.__unicode__().encode("ascii")

    # Python 3
    else:

        def __str__(self):
            return "[Error %d] %s; called with %r" % (
                self.code, self.__doc__.rstrip("."), self.args)


class NameTooLongError(LockingError):
    """Recipient name too long."""

    code = L_NAMELEN


class TempLockError(LockingError):
    """Error creating tmp lockfile."""

    code = L_TMPLOCK


class TempLockWriteError(LockingError):
    """Can't write pid into tmp lockfile."""

    code = L_TMPWRITE


class MaxAttemptsError(LockingError):
    """Failed after max. number of attempts."""

    code = L_MAXTRYS


class UnknownError(LockingError):
    """Unknown error; check errno."""

    code = L_ERROR


class MandatoryLockError(LockingError):
    """Cannot set mandatory lock on tempfile."""

    code = L_MANLOCK


errors = {
    error.code: error
    for error in LockingError.__subclasses__()
}


class FileSystemString(ctypes.c_char_p):
    """`ctypes` argument type to transparently encode Unicode strings.

    Specifically, Unicode strings are transparently encoded using the
    file-system encoding. All other object types are passed up to
    `ctypes.c_char_p`.
    """

    @classmethod
    def from_param(cls, obj):
        if isinstance(obj, type("text")):
            enc = sys.getfilesystemencoding()
            obj = obj.encode(enc)
        return super(FileSystemString, cls).from_param(obj)


def _check_create(result, func, arguments):
    if result != 0:
        raise errors[result](*arguments)


def _check_remove(result, func, arguments):
    if result != 0:
        errno = ctypes.get_errno()
        raise OSError(errno, os.strerror(errno), *arguments)


def _check_touch(result, func, arguments):
    if result != 0:
        errno = ctypes.get_errno()
        raise OSError(errno, os.strerror(errno), *arguments)


def _check_check(result, func, arguments):
    return result == 0


# int     lockfile_create(const char *lockfile, int retries, int flags);
lockfile_create = liblockfile.lockfile_create
lockfile_create.argtypes = (FileSystemString, ctypes.c_int, ctypes.c_int)
lockfile_create.errcheck = _check_create

# int     lockfile_remove(const char *lockfile);
lockfile_remove = liblockfile.lockfile_remove
lockfile_remove.argtypes = (FileSystemString,)
lockfile_remove.errcheck = _check_remove

# int     lockfile_touch(const char *lockfile);
lockfile_touch = liblockfile.lockfile_touch
lockfile_touch.argtypes = (FileSystemString,)
lockfile_touch.errcheck = _check_touch

# int     lockfile_check(const char *lockfile, int flags);
lockfile_check = liblockfile.lockfile_check
lockfile_check.argtypes = (FileSystemString, ctypes.c_int)
lockfile_check.errcheck = _check_check


class Lock:
    """Manage a lock file with ``liblockfile``."""

    def __init__(self, filename, retries=0):
        self.filename = filename
        self.retries = retries
        self.flags = 0

    @classmethod
    def WithPID(cls, filename, retries=0):
        lockfile = cls(filename, retries)
        lockfile.flags |= L_PID
        return lockfile

    @classmethod
    def WithPPID(cls, filename, retries=0):
        lockfile = cls(filename, retries)
        lockfile.flags |= L_PPID
        return lockfile

    def create(self):
        lockfile_create(self.filename, self.retries, self.flags)

    def remove(self):
        lockfile_remove(self.filename)

    def touch(self):
        lockfile_touch(self.filename)

    def check(self):
        return lockfile_check(self.filename, self.flags)

    def __enter__(self):
        self.create()
        return self

    def __exit__(self, *exc_info):
        self.remove()


class LockHolder:
    """Holds a `Lock` by periodically touching it.

    Use like so::

      with Lock("file.lock") as lock, LockHolder(lock):
          ...

    """

    def __init__(self, lock):
        self.lock = lock
        self._release = threading.Event()
        self._holder = None

    def _hold(self):
        while not self._release.wait(60):
            self.lock.touch()

    def __enter__(self):
        self._release.clear()
        self._holder = threading.Thread(target=self._hold)
        self._holder.setDaemon(True)
        self._holder.start()
        return self

    def __exit__(self, *exc_info):
        self._release.set()
        self._holder.join()
        self._holder = None
