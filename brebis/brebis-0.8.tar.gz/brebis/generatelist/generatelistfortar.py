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

# Generate a list of files from a tar archive
'''Generate a list of files from a tar archive'''

import logging
import os.path
import tarfile

from brebis.generatelist.generatelist import GenerateList
from brebis.checkhashes import get_hash

class GenerateListForTar(GenerateList):
    '''Generate a list of files from a tar archive'''

    def __init__(self, __genparams):
        '''The constructor for the GenerateListForTar class'''
        self.__arcpath = __genparams['arcpath']
        self.__delimiter = __genparams['delimiter']
        self._genfull = __genparams['genfull']
        try:
            __tar = tarfile.open(self.__arcpath, 'r')
            self.__main(__tar)
        except (tarfile.TarError, EOFError) as _msg:
            __warn = '. You should investigate for a data corruption.'
            logging.warning('{}: {}{}'.format(self.__arcpath, str(_msg), __warn))

    def __main(self, __tar):
        '''Main for the GenerateListForTar class'''
        __listoffiles = ['[files]\n']
        __oneline = '{value}{delimiter} ={value} uid{delimiter}{value} gid{delimiter}{value} mode{delimiter}{value} type{delimiter}{value}\n'.format(value='{}', delimiter=self.__delimiter)
        __onelinewithhash = '{value}{delimiter} ={value} uid{delimiter}{value} gid{delimiter}{value} mode{delimiter}{value} type{delimiter}{value} md5{delimiter}{value}\n'.format(value='{}', delimiter=self.__delimiter)
        __onelinewithtarget = '{value}{delimiter} ={value} uid{delimiter}{value} gid{delimiter}{value} mode{delimiter}{value} type{delimiter}{value} md5{delimiter}{value} target{delimiter}{value}\n'.format(value='{}', delimiter=self.__delimiter)
        for __tarinfo in __tar:
            # Pick up tar information
            __tarinfo.name = self._normalize_path(__tarinfo.name)
            __type = self.__translate_type(__tarinfo.type)
            __mode = oct(__tarinfo.mode).split('o')[-1]
            # if the file has no right, need to manipulate the output - solving #15
            if __mode == '0':
                __mode = '000'
            if __type == 'f':
                # extract hash sum of the file inside the archive
                __hash = get_hash(__tar.extractfile(__tarinfo.name), 'md5')
                # format the retrieved information
                __listoffiles.append(__onelinewithhash.format(__tarinfo.name,
                                                        str(__tarinfo.size),
                                                        str(__tarinfo.uid),
                                                        str(__tarinfo.gid),
                                                        __mode,
                                                        __type,
                                                        __hash,
                                                        __tarinfo.linkname))
            elif __type == 'l' or __type == 's':
                # extract hash sum of the file inside the archive
                __hash = get_hash(__tar.extractfile(__tarinfo.name), 'md5')
                # format the retrieved information
                __listoffiles.append(__onelinewithtarget.format(__tarinfo.name,
                                                        str(__tarinfo.size),
                                                        str(__tarinfo.uid),
                                                        str(__tarinfo.gid),
                                                        __mode,
                                                        __type,
                                                        __hash,
                                                        __tarinfo.linkname))
            else:
                # if file is not regular file, ignoring its hash sum
                __listoffiles.append(__oneline.format(__tarinfo.name,
                                                        str(__tarinfo.size),
                                                        str(__tarinfo.uid),
                                                        str(__tarinfo.gid),
                                                        __mode,
                                                        __type))
        # Compose the name of the generated list
        if self.__arcpath.lower().endswith('.tar'):
            self.__arclistpath = ''.join([self.__arcpath[:-3], 'list'])
            if self._genfull:
                self.__arcconfpath = ''.join([self.__arcpath[:-3], 'conf'])
                self.__arcname = os.path.basename(self.__arcpath[:-4])
        elif self.__arcpath.lower().endswith('.tar.gz'): 
            self.__arclistpath = ''.join([self.__arcpath[:-6], 'list'])
            if self._genfull:
                self.__arcconfpath = ''.join([self.__arcpath[:-6], 'conf'])
                self.__arcname = os.path.basename(self.__arcpath[:-7])
        elif self.__arcpath.lower().endswith('.tar.bz2'):
            self.__arclistpath = ''.join([self.__arcpath[:-7], 'list'])
            if self._genfull:
                self.__arcconfpath = ''.join([self.__arcpath[:-7], 'conf'])
                self.__arcname = os.path.basename(self.__arcpath[:-8])
        elif self.__arcpath.lower().endswith('.tar.xz'):
            self.__arclistpath = ''.join([self.__arcpath[:-6], 'list'])
            if self._genfull:
                self.__arcconfpath = ''.join([self.__arcpath[:-6], 'conf'])
                self.__arcname = os.path.basename(self.__arcpath[:-7])
        elif self.__arcpath.lower().endswith('.tgz'):
            self.__arclistpath = ''.join([self.__arcpath[:-3], 'list'])
            if self._genfull:
                self.__arcconfpath = ''.join([self.__arcpath[:-3], 'conf'])
                self.__arcname = os.path.basename(self.__arcpath[:-4])
        elif self.__arcpath.lower().endswith('.tbz'):
            self.__arclistpath = ''.join([self.__arcpath[:-3], 'list'])
            if self._genfull:
                self.__arcconfpath = ''.join([self.__arcpath[:-3], 'conf'])
                self.__arcname = os.path.basename(self.__arcpath[:-4])
        elif self.__arcpath.lower().endswith('.tbz2'):
            self.__arclistpath = ''.join([self.__arcpath[:-4], 'list'])
            if self._genfull:
                self.__arcconfpath = ''.join([self.__arcpath[:-4], 'conf'])
                self.__arcname = os.path.basename(self.__arcpath[:-5])
        # call the method to write information in a file
        __listconfinfo = {'arclistpath': self.__arclistpath,
                                'listoffiles':__listoffiles}
        self._generate_list(__listconfinfo)
        # call the method to write the configuration file if --gen-full was required
        if self._genfull:
            # generate the hash sum of the list of files
            __listhashsum = self._get_list_hash(__listconfinfo['arclistpath'])
            __confinfo = {'arcname':self.__arcname,
                            'arcpath':self.__arcpath,
                            'arcconfpath': self.__arcconfpath,
                            'arclistpath': self.__arclistpath,
                            'arctype': 'archive',
                            'sha512': __listhashsum}
            self._generate_conf(__confinfo)

    def __translate_type(self, __arctype):
        '''Translate the type of the file inside the tar by a generic
        name
        '''
        __types = {tarfile.REGTYPE: 'f',
            tarfile.AREGTYPE: 'a',
            tarfile.CHRTYPE: 'c',
            tarfile.DIRTYPE: 'd',
            tarfile.LNKTYPE: 'l',
            tarfile.SYMTYPE: 's',
            tarfile.CONTTYPE: 'n',
            tarfile.BLKTYPE: 'b',
            tarfile.GNUTYPE_SPARSE: 'g',
            tarfile.FIFOTYPE: 'o'}
        return __types[__arctype]

