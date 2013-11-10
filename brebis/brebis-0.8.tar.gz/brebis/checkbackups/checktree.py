# -*- coding: utf-8 -*-
# Copyright © 2013 Carl Chenet <chaica@ohmytux.com>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Check a file tree
'''Check a file tree'''

import os
import stat

from brebis.expectedvalues import ExpectedValues
from brebis.checkbackups.checkarchive import CheckArchive

class CheckTree(CheckArchive):
    '''Check a file tree'''

    def _main(self, _cfgvalues, _options):
        '''Main for CheckTree'''
        _data = []
        self.__treepath = _cfgvalues['path']
        _data, __arcdata = ExpectedValues(_cfgvalues, _options).data
        # Save the tree root to determine the relative path in the file tree
        self.__treepath = self.__treepath
        for __dirpath, __dirnames, __filenames, in os.walk(_cfgvalues['path']):
            __dirinfo = os.lstat(__dirpath)
            __dirmode = stat.S_IMODE(__dirinfo.st_mode)
            # Translate file type in brebis intern file type
            __type = self.__translate_type(__dirinfo.st_mode)
            # Extract file data
            __arcinfo = {'path': os.path.relpath(__dirpath, self.__treepath),
                        'size': __dirinfo.st_size, 'uid': __dirinfo.st_uid,
                        'gid': __dirinfo.st_gid, 'mode': __dirmode,
                        'type': __type}
            _data = self._check_path(__arcinfo, _data)
            for __filename in __filenames:
                __filepath = os.path.join(__dirpath, __filename)
                __filepath = self._normalize_path(__filepath)
                self.__fileinfo = os.lstat(__filepath)
                __filemode = stat.S_IMODE(self.__fileinfo.st_mode)
                __type = self.__translate_type(self.__fileinfo.st_mode)
                if __type == 's':
                    __arcinfo = {'path': os.path.relpath(__filepath, self.__treepath),
                                'size': self.__fileinfo.st_size, 'uid': self.__fileinfo.st_uid,
                                'gid': self.__fileinfo.st_gid, 'mode': __filemode,
                                'type': __type, 'target': os.readlink(__filepath)}
                else:
                    __arcinfo = {'path': os.path.relpath(__filepath, self.__treepath),
                                'size': self.__fileinfo.st_size, 'uid': self.__fileinfo.st_uid,
                                'gid': self.__fileinfo.st_gid, 'mode': __filemode,
                                'type': __type}
                _data = self._check_path(__arcinfo, _data)
        self._missing_files = [_file['path'] for _file in _data]

    def __translate_type(self, __mode):
        '''Translate the type of the file to a generic name'''
        if stat.S_ISREG(__mode):
            if self.__fileinfo[stat.ST_NLINK] > 1:
                return 'l'
            else:
                return 'f'
        elif stat.S_ISDIR(__mode):
            return 'd'
        elif stat.S_ISCHR(__mode):
            return 'c'
        elif stat.S_ISLNK(__mode):
            return 's' 
        elif stat.S_BLK(__mode):
            return 'b'
        elif stat.S_ISSOCK(__mode):
            return 'k'
        elif stat.S_ISFIFO(__mode):
            return 'o'

    def _extract_stored_file(self, __arcfilepath):
        '''extract a file from the tree and return a file object'''
        if os.path.isabs(__arcfilepath):
            __file = open(__arcfilepath, 'rb')
        else:
            __fullpath = os.path.normpath(os.path.join(self.__treepath, __arcfilepath))
            __file = open(__fullpath, 'rb')
        return __file
