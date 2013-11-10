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

# Check a zip archive
'''Check a zip archive'''

import sys
import zipfile
import logging
import stat

from brebis.checkbackups.checkarchive import CheckArchive
from brebis.expectedvalues import ExpectedValues
from brebis.identifylimitations import IdentifyLimitations

class CheckZip(CheckArchive):
    '''Check a zip archive'''

    def _main(self, _cfgvalues, _options):
        '''Main for CheckZip'''
        _crcerror = ''
        _data = []
        _data, __arcdata = ExpectedValues(_cfgvalues, _options).data
        #########################
        # Test the archive itself
        #########################
        self._archive_checks(__arcdata, _cfgvalues['path'])
        try:
            self._zip = zipfile.ZipFile(_cfgvalues['path'], 'r', allowZip64=True)
            ###############################
            # Test the files in the archive
            ###############################
            if _data:
                # Identify limitations given the features asked by the user
                # retrieve every keys of every files in _data
                configkeys = set()
                for i in _data:
                    configkeys = configkeys | set(i.keys())
                IdentifyLimitations(_cfgvalues['path'], 'zip', configkeys)
                _crcerror = self._zip.testzip()
                if _crcerror:
                    logging.warning('{} has at least one file corrupted:{}'.format(_cfgvalues['path'], _crcerror))
                else:
                    _zipinfo = self._zip.infolist()
                    for _fileinfo in _zipinfo:
                        _fileinfo.filename = self._normalize_path(_fileinfo.filename)
                        __uid, __gid = self.__extract_uid_gid(_fileinfo)
                        __type = self.__translate_type(_fileinfo.external_attr >> 16)
                        __arcinfo = {'path': _fileinfo.filename, 'size': _fileinfo.file_size,
                                        'mode': stat.S_IMODE((_fileinfo.external_attr >> 16)),
                                        'uid': __uid, 'gid': __gid, 'type': __type}
                        _data = self._check_path(__arcinfo, _data)
                    self._missing_files = [_file['path'] for _file in _data]
        except zipfile.BadZipfile as _msg:
            __warn = '. You should investigate for a data corruption.'
            logging.warning('{}: {}{}'.format(_cfgvalues['path'], str(_msg), __warn))

    def _extract_stored_file(self, __arcfilepath):
        '''Extract a file from the archive and return a file object'''
        __file = self._zip.open(__arcfilepath, 'r')
        return __file

    def __extract_uid_gid(self, __binary):
        '''Extract uid and gid from a zipinfo.extra object (platform dependant)'''
        __uid, __gid = int.from_bytes(__binary.extra[15:17], 'little'), \
                            int.from_bytes(__binary.extra[20:22], 'little')
        return (__uid, __gid)

    def __translate_type(self, __mode):
        '''Translate the type of the file to a generic name'''
        if stat.S_ISREG(__mode):
            return 'f'
        elif stat.S_ISDIR(__mode):
            return 'd'
