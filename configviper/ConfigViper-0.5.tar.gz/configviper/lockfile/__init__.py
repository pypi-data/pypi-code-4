# -*- coding: utf-8 -*-
#
# src/configviper/lockfile/__init__.py
# https://bitbucket.org/danielgoncalves/configviper
#
# ConfigViper  Copyright (C) 2013  Daniel Gonçalves <daniel@base4.com.br>
#
# This file is part of ConfigViper.
#
# ConfigViper is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as 
# published by the Free Software Foundation, either version 3 of the 
# License, or (at your option) any later version.
#
# ConfigViper is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with ConfigViper. If not, see <http://www.gnu.org/licenses/>.
#

"""
Cross-platform (posix/windows) API for flock-style file locking.
This implementation is based on Roundup Issue-Tracking System 
`ctypes port <http://sourceforge.net/p/roundup/code/ci/default/tree/roundup/>`_,
which in turn, is based on an Active State's Python Recipe 
`portalocker <http://code.activestate.com/recipes/65203/>`_.
"""

__all__ = ['ctypeslocker', 'posixlocker',]

import codecs
import os


class LockError(Exception):
    def __init__(self, *args, **kwargs):
        super(LockError, self).__init__(*args, **kwargs)


class UnlockError(Exception):
    def __init__(self, *args, **kwargs):
        super(UnlockError, self).__init__(*args, **kwargs)


class NoLockImplementationError(Exception):
    def __init__(self, *args, **kwargs):
        super(NoLockImplementationError, self).__init__(*args, **kwargs)


class PortaLocker(object):
    """Base class for actual file lock implementations."""

    def __init__(self, filename, mode, 
            encoding='utf-8', 
            ignore_encoding=False,
            sync_before_unlock=True):
        super(PortaLocker, self).__init__()
        self.filename = filename
        self.mode = mode
        self.encoding = encoding
        self.ignore_encoding = ignore_encoding
        self.sync_before_unlock = sync_before_unlock
        self.file_object = None
        self.is_locked = False


    def lock(self):
        """Open file and attempt to lock it. Returns ``True`` on success."""
        self._open()
        try:
            if self._lock_impl():
                return True
            else:
                self._close()
                return False
        except:
            self._close()
            raise


    def unlock(self):
        """Attempt to unlock and close the file."""
        try:
            if self.sync_before_unlock:
                self._sync()
            success = self._unlock_impl()
            self._close()
        except:
            self._close()
            raise
        return success


    def _lock_impl(self):
        # implementations should override this method
        raise NotImplementedError('lock() method not yet implemented!')


    def _unlock_impl(self):
        # implementations should override this method
        raise NotImplementedError('unlock() method not yet implemented!')


    def _open(self):
        if self.ignore_encoding:
            self.file_object = open(self.filename, self.mode)
        else:
            self.file_object = codecs.open(self.filename, self.mode,
                    encoding=self.encoding)


    def _close(self):
        if self.file_object is not None:
            if not self.file_object.closed:
                self.file_object.close()


    def _sync(self):
        if self.file_object is not None:
            if not self.file_object.closed:
                self.file_object.flush()
                os.fsync(self.file_object.fileno())


    def __enter__(self):
        if not self.lock():
            raise LockError('Cannot lock file: %s' % self.filename)
        self.is_locked = True
        return self


    def __exit__(self, type, value, traceback):
        if self.is_locked:
            if not self.unlock():
                raise UnlockError('Cannot unlock file: %s' % self.filename)
            self.is_locked = False


def lockfile(filename, mode, encoding='utf-8', ignore_encoding=False):
    """Attempt to instantiate and return an appropriate file lock implementation
    which depends on the underlying operating system. The best way to use the
    returned implementation is in a managed context with ``with`` statement or
    use the methods :meth:`~PortaLocker.lock` and :meth:`~PortaLocker.unlock`
    directly::

        with lockfile('/home/john/eggs.txt', 'wb') as locker:
            # here, eggs.txt was opened and the file-like object can be
            # accessed through locker.file_object attribute, e.g.:
            locker.file_object.write(data)

    When the context ends, the file is unlocked and closed, in that order.

    :param filename: String. The full path name to the file that should be
            locked. The file will be opened using the ``mode`` parameter and
            then locked.

    :param mode: String. The mode as in ``codecs.open`` or ``open``.

    :param encoding: String. The encoding which is to be used for the file, as
            in ``codecs.open`` ``encoding`` parameter. This parameter will be
            ignored if ``ignore_encoding`` is ``True``.

    :param ignore_encoding: Boolean. If ``False``, which is the default, the
            file will be opened with ``codecs.open``. Otherwise, the file will
            be opened with the Python's ``open`` built-in function.
    """
    args = (filename, mode,)
    kwargs = {'encoding': encoding, 'ignore_encoding': ignore_encoding,}

    if is_fcntl_available():
        from posixlocker import PosixPortaLocker
        return PosixPortaLocker(*args, **kwargs)

    elif is_windows(): 
        from ctypeslocker import CTypesPortaLocker
        return CTypesPortaLocker(*args, **kwargs)
    
    raise NoLockImplementationError('There is no suitable lock implementation '
            '(os.name="%s")' % os.name)


def is_fcntl_available():
    try:
        import fcntl
        return True
    except ImportError:
        return False
    

def is_windows():
    names = ('nt', 'win', 'winnt', 'win32', 'windows', 'windowsnt')
    return os.name.lower() in names
