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

# Extract information about the archive (if it is one) and expected saved files
'''Extract information about the archive (if it is one) and expected saved files'''

import logging
import os
import sys
import configparser
from configparser import ConfigParser
from hashlib import algorithms_guaranteed
from brebis.checkfilelist import CheckFileList

class ExpectedValues(object):
    '''Extract information about the archive (if it is one)
    and expected saved files.
    '''

    def __init__(self, __bckconf, __options):
        '''The constructor of the ExpectedValues class.
        '''
        self.__bckfiles= []
        self.__arcdata = {}
        __path = __bckconf['files_list']
        # Define delimiter value
        if not __bckconf['delimiter']:
            __delimiter = __options.delimiter
        else:
            __delimiter = __bckconf['delimiter']
        # test if the expected value of the hash of the list of file is correct
        CheckFileList(__bckconf)
        # launch the main of the class
        self.__main(__path, __delimiter)

    def __main(self, __path, __delimiter):
        '''Main of the ExpectedValues class'''
        try:
            with open(__path, 'r') as __file:
                self.__retrieve_data(__file, __path, __delimiter)
        except (configparser.Error, IOError, OSError) as __err:
            print(__err)
            sys.exit(1)

    def __retrieve_data(self, __file, __path, __delimiter):
        '''Retrieve data from the expected files'''
        # Using default delimiter
        __config = ConfigParser(delimiters=(__delimiter))
        __config.optionxform = str
        __config.read_file(__file)
        #########################
        # Test the archive itself
        #########################
        if __config.has_section('archive'):
            __archive = __config.items('archive')
            # Testing the size of the archive
            if 'size' in __config['archive']:
                ### Test if the equality is required
                if __config['archive']['size'].startswith('='):
                    self.__arcdata['equals'] = self.__convert_arg(__config['archive']['size'])
                ### Test if bigger than is required
                elif __config['archive']['size'].startswith('>'):
                    self.__arcdata['biggerthan'] = self.__convert_arg(__config['archive']['size'])
                ### Test if smaller than is required
                elif __config['archive']['size'].startswith('<'):
                    self.__arcdata['smallerthan'] = self.__convert_arg(__config['archive']['size'])
            # Test the mode of the archive
            if 'mode' in __config['archive']:
                if len(__config['archive']['mode']) < 3 or len(__config['archive']['mode']) > 4:
                    logging.warning('{}: Wrong format for the mode.'.format(__path))
                else:
                    self.__arcdata['mode'] = __config['archive']['mode']
            try:
                # Testing the uid of the archive
                if 'uid' in __config['archive']:
                    self.__arcdata['uid'] = int(__config['archive']['uid'])
                # Testing the gid of the archive
                if 'gid' in __config['archive']:
                    self.__arcdata['gid'] = int(__config['archive']['gid'])
            except ValueError as __msg:
                logging.warning(__msg)
            # Testing the hash of the archive
            for __hash in algorithms_guaranteed:
                if __hash in __config['archive']:
                        self.__arcdata['hash'] = {'hashtype':__hash, 'hashvalue':__config['archive'][__hash]}
        ######################
        # Test expected  files
        ######################
        if __config.has_section('files'):
            __files = __config.items('files')
            for __fileitems in __files:
                __data = {}
                __data['path'] = __fileitems[0]
                if __data['path'].endswith('/'):
                    __data['path'] = __data['path'][:-1]
                if len(__fileitems) == 2:
                    for __item in __fileitems[1].split(' '):
                        try:
                            # Testing the items for an expected file
                            if __item == 'unexpected':
                                __data['unexpected'] = True
                            # The uid of the expected file
                            elif __item.startswith('uid{}'.format(__delimiter)):
                                __data['uid'] = int(__item.split(__delimiter)[-1])
                            # The gid of the expected file
                            elif __item.startswith('gid{}'.format(__delimiter)):
                                __data['gid'] = int(__item.split(__delimiter)[-1])
                            # The mode of the expected file
                            elif __item.startswith('mode{}'.format(__delimiter)):
                                __mode =__item.split(__delimiter)[-1]
                                if len(__mode) < 3 or len(__mode) > 4:
                                    logging.warning('{}: Wrong format for the mode.'.format(__data['path']))
                                else:
                                    __data['mode'] = __mode
                            # Testing the type of the file
                            elif __item.startswith('type{}'.format(__delimiter)):
                                __type =__item.split(__delimiter)[-1]
                                ### f for file, c for character, d for directory
                                ### s for symbolink link, b for block, o for fifo,
                                ### k for socket, l for hard link
                                __types = ('f','c','d','s','b','o','k', 'l')
                                if __type not in __types:
                                    logging.warning('{}: Unknown type {} for file parameter'.format(__data['path'], __type))
                                else:
                                    __data['type'] = __type
                            # Testing the size of the file
                            ### Test if the equality is required
                            elif __item.startswith('='):
                                __data['equals'] = self.__convert_arg(__item)
                            ### Test if bigger than is required
                            elif __item.startswith('>'):
                                __data['biggerthan'] = self.__convert_arg(__item)
                            ### Test if smaller than is required
                            elif __item.startswith('<'):
                                __data['smallerthan'] = self.__convert_arg(__item)
                            # Testing if there is a target for this file
                            elif __item.startswith('target{}'.format(__delimiter)):
                                if __data['type'] and (__data['type'] == 'l' or __data['type'] == 's'):
                                    __data['target'] = __item.split(__delimiter)[-1]
                                else:
                                    __errmsg = 'The list of your file contains a target field although the file is not a symlink or a hard link'
                                    print(__errmsg)
                                    sys.exit(1)
                            # Test if a hash is provided for this file
                            for __hash in algorithms_guaranteed:
                                if __item.startswith('{}{}'.format(__hash, __delimiter)):
                                    __hashtype, __hashvalue = __item.split(__delimiter)
                                    __data['hash'] = {'hashtype':__hashtype, 'hashvalue':__hashvalue}
                        except ValueError as __msg:
                            logging.warning(__msg)
                self.__bckfiles.append(__data)

    def __convert_arg(self, __arg):
        '''Convert the given file length to bytes'''
        __res = 0
        __arg = ''.join([__arg[:-1], __arg[-1].lower()])
        try:
            for __value, __power in [('k', 1),('m', 2),('g', 3),('p', 4),
                                        ('e', 5),('z', 6),('y', 7)]:
                if __arg.endswith(__value):
                    __res = int(__arg[1:-1]) * 1024**__power
            if __res == 0:
                __res = int(__arg[1:])
        except ValueError as __msg:
            print(__msg)
            logging.warning(__msg)
            __res = 0
        finally:
            return __res

    @property
    def data(self):
        '''Return the paths of the expected files in the archive'''
        return self.__bckfiles, self.__arcdata
