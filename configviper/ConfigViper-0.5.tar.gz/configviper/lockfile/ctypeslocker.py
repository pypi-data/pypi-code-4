# -*- coding: utf-8 -*-
#
# src/configviper/lockfile/ctypeslocker.py
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

import msvcrt

from ctypes import *
from ctypes.wintypes import BOOL, DWORD, HANDLE

from . import PortaLocker

LOCK_SH = 0     # default
LOCK_NB = 0x1   # LOCKFILE_FAIL_IMMEDIATELY
LOCK_EX = 0x2   # LOCKFILE_EXCLUSIVE_LOCK

# detect size of ULONG_PTR
# (!) based on code from pyserial project [http://pyserial.sourceforge.net/]
def is_64bit():
    return sizeof(c_ulong) != sizeof(c_void_p)

PVOID = c_void_p

if is_64bit():
    ULONG_PTR = c_int64
else:
    ULONG_PTR = c_ulong

# Union-within-Structure syntax in ctypes
# (!) from stackoverflow [http://stackoverflow.com/a/3480860/550237]
class _OFFSET(Structure):
    _fields_ = [
            ('Offset', DWORD),
            ('OffsetHigh', DWORD),]

class _OFFSET_UNION(Union):
    _anonymous_ = ['_offset']
    _fields_ = [
            ('_offset', _OFFSET),
            ('Pointer', PVOID),]

class OVERLAPPED(Structure):
    _anonymous_ = ['_offset_union']
    _fields_ = [
            ('Internal', ULONG_PTR),
            ('InternalHigh', ULONG_PTR),
            ('_offset_union', _OFFSET_UNION),
            ('hEvent', HANDLE),]

LPOVERLAPPED = POINTER(OVERLAPPED)

# define function prototypes for extra safety
LockFileEx = windll.kernel32.LockFileEx
LockFileEx.restype = BOOL
LockFileEx.argtypes = [HANDLE, DWORD, DWORD, DWORD, DWORD, LPOVERLAPPED]
UnlockFileEx = windll.kernel32.UnlockFileEx
UnlockFileEx.restype = BOOL
UnlockFileEx.argtypes = [HANDLE, DWORD, DWORD, DWORD, LPOVERLAPPED]

class CTypesPortaLocker(PortaLocker):
    """File lock implementation targeting Windows :sup:`TM` based on ``ctypes``
    Python package, using underlying ``LockFileEx`` and ``UnlockFileEx``
    functions.
    """

    def __init__(self, filename, mode, encoding='utf-8', ignore_encoding=False):
        super(CTypesPortaLocker, self).__init__(
                filename, mode,
                encoding=encoding,
                ignore_encoding=ignore_encoding)


    def _lock_impl(self):
        hfile = msvcrt.get_osfhandle(self.file_object.fileno())
        overlapped = OVERLAPPED()
        if LockFileEx(hfile, LOCK_EX, 0, 0, 0xFFFF0000, byref(overlapped)):
            return True
        return False


    def _unlock_impl(self):
        hfile = msvcrt.get_osfhandle(self.file_object.fileno())
        overlapped = OVERLAPPED()
        if UnlockFileEx(hfile, 0, 0, 0xFFFF0000, byref(overlapped)):
            return True
        return False
