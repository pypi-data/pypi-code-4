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

# Check a bzip2 archive
'''Check a bzip2 archive'''

import sys
import logging
import os.path
import bz2

from brebis.checkbackups.checkarchive import CheckArchive
from brebis.expectedvalues import ExpectedValues
from brebis.identifylimitations import IdentifyLimitations

class CheckBzip2(CheckArchive):
    '''Check a bzip2 archive'''

    def _main(self, _cfgvalues, _options):
        '''Main for CheckBzip2'''
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
            IdentifyLimitations(_cfgvalues['path'], 'bz2', configkeys)
            ##############################################
            # Looking for data corruption
            # Have to read the whole archive to check CRC
            ##############################################
            try:
                with bz2.BZ2File(_cfgvalues['path'], 'r') as __bz2:
                    __bz2.read()
            except IOError as __msg:
                __warn = '. You should investigate for a data corruption.'
                logging.warning('{}: {}{}'.format(_cfgvalues['path'], str(__msg), __warn))
            else:
                __name = os.path.split(_cfgvalues['path'])[-1].split('.')[0]
                # Bzip2 does not allow to know the compressed file size, default to 0
                __arcinfo = {'path': __name, 'type': 'f', 'size': 0}
                _data = self._check_path(__arcinfo, _data)
                self._missing_files = [_file['path'] for _file in _data]

    def _extract_stored_file(self, __nouse):
        '''Extract a file from the archive and return a file object'''
        __fileobj = bz2.BZ2File(self.__arcpath, 'r')
        return __fileobj

