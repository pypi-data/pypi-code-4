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

import gzip
import os
import os.path
import stat

from brebis.checkhashes import get_hash
from brebis.generatelist.generatelist import GenerateList

# Generate a list of files from a gzip archive
'''Generate a list of files from a gzip archive'''

class GenerateListForGzip(GenerateList):
    '''Generate a list of files from a gzip archive'''

    def __init__(self, __genparams):
        '''The constructor for the GenerateListForGzip class'''
        __arcpath = __genparams['arcpath']
        __delimiter = __genparams['delimiter']
        self._genfull = __genparams['genfull']
        __listoffiles = ['[files]\n']
        __fileinfo = os.lstat(__arcpath)
        __filetype = 'f'
        __filehash = get_hash(gzip.open(__arcpath, 'rb'), 'md5')
        with open(__arcpath, 'rb') as __gzip:
            __filesize = self.__extract_size(__gzip)
            __filename = self.__extract_initial_filename(__gzip,
                        os.path.split(__arcpath)[-1][:-2])
        __onelinewithhash = '{value}{delimiter} ={value} type{delimiter}{value} md5{delimiter}{value}\n'.format(value='{}', delimiter=__delimiter)
        __listoffiles.append(__onelinewithhash.format(
                                __filename,
                                str(__filesize),
                                __filetype,
                                __filehash))
        # call the method to write information in a file
        __listconfinfo = {'arclistpath': ''.join([__arcpath[:-2], 'list']),
                            'listoffiles':  __listoffiles}
        self._generate_list(__listconfinfo)
        # call the method to write the configuration file if --gen-full was required
        if self._genfull:
            # generate the hash sum of the list of files
            __listhashsum = self._get_list_hash(__listconfinfo['arclistpath'])
            __arcname =  os.path.basename(__arcpath[:-3])
            __confinfo = {'arcname': __arcname,
                            'arcpath': __arcpath,
                            'arcconfpath': ''.join([__arcpath[:-2],'conf']),
                            'arclistpath': __listconfinfo['arclistpath'],
                            'arctype': 'archive',
                            'sha512': __listhashsum}
            self._generate_conf(__confinfo)

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
