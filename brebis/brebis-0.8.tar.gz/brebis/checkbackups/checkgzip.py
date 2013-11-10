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

# Check a gzip archive
'''Check a gzip archive'''

import sys
import logging
import os.path
import gzip

from brebis.checkbackups.checkarchive import CheckArchive
from brebis.expectedvalues import ExpectedValues
from brebis.identifylimitations import IdentifyLimitations

class CheckGzip(CheckArchive):
    '''Check a gzip archive'''

    def _main(self, _cfgvalues, _options):
        '''Main for CheckGzip'''
        _data = []
        _data, __arcdata = ExpectedValues(_cfgvalues, _options).data
        self.__arcpath = _cfgvalues['path']
        #########################
        # Test the archive itself
        #########################
        self._archive_checks(__arcdata, _cfgvalues['path'])
        ###############################
        # Test the file in the archive
        ###############################
        if _data:
            # Identify limitations given the features asked by the user
            # retrieve every keys of every files in _data
            configkeys = set()
            for i in _data:
                configkeys = configkeys | set(i.keys())
            IdentifyLimitations(_cfgvalues['path'], 'gz', configkeys)
            ##############################################
            # Looking for data corruption
            # Have to read the whole archive to check CRC
            ##############################################
            try:
                with gzip.open(_cfgvalues['path'], 'rb') as __gzip:
                    __gzip.read()
            except IOError as __msg:
                __warn = '. You should investigate for a data corruption.'
                logging.warning('{}: {}{}'.format(_cfgvalues['path'], str(__msg), __warn))
            else:
                ########################################
                # No corruption, extracting information
                ########################################
                with open(_cfgvalues['path'], 'rb') as __gzip:
                    __filesize = self.__extract_size(__gzip)
                    __name = self.__extract_initial_filename(__gzip,
                                os.path.split(_cfgvalues['path'])[-1].rstrip('.gz'))
                    __arcinfo = {'path': __name, 'size': __filesize, 'type': 'f'}
                    _data = self._check_path(__arcinfo, _data)
                    self._missing_files = [_file['path'] for _file in _data]

    def __extract_size(self, __binary):
        '''Extract the size of the uncompressed file inside the archive -
        4 last bytes of the archive
        '''
        __binary.seek(-4, 2)
        return int.from_bytes(__binary.read(), 'little')

    def __extract_initial_filename(self, __binary, __arcname):
        '''Extract initial filename of the uncompressed file'''
        # We move the cursor on the 4th byte
        __binary.seek(3,0)
        # Read a byte
        __flag = __binary.read(1)
        # Store flag byte
        __intflag = int.from_bytes(__flag,'little')
        # If the extra field flag is on, extract the size of its data field
        __extralen = 0
        if __intflag & 4 != 0:
            __binary.seek(9,0)
            __extralenbyte = __binary.read(2)
            __extralen = int.from_byte(__extralenbyte,'little') + 2
        # If the flag "name" is on, skip to it and read the associated content
        __binaryname = b''
        if __intflag & 8 != 0:
            __binary.seek(10 + __extralen)
            # until zero byte is found, read the initial filename in bytes
            while True:
                __newbyte = __binary.read(1)
                if __newbyte != b'\x00':
                    __binaryname += __newbyte
                else:
                    break
            return __binaryname.decode('latin1')
        else:
            return __arcname

    def _extract_stored_file(self, __arcfilepath):
        '''Extract a file from the archive and return a file object'''
        __fileobj = gzip.open(self.__arcpath, 'rb')
        return __fileobj
