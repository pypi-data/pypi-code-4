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

# Identify limitations for this archive type given the checks asked by the user
'''Identify limitations for this archive type given the 
checks asked by the user'''

import logging

class IdentifyLimitations:
    '''Identify limitations for this archive type given the 
    checks asked by the user'''

    def __init__(self, __arcpath, __arctype, __data):
        self.__data = __data
        self.__arcpath = __arcpath
        self.__main(__arctype)

    def __main(self, __arctype):
        '''Main for IdentifyLimitations'''
        getattr(self, ''.join(['_IdentifyLimitations__study_', __arctype]))()

    def __study_gz(self):
        '''Study the required checks for the gzip archive type'''
        __unsupported_gz = {'uid', 'gid', 'mode', 'target'}
        for __param in self.__data:
            if __param in __unsupported_gz:
                self.__warn(__param)

    def __study_bz2(self):
        '''Study the required checks for the gzip archive type'''
        __unsupported_bz2 = {'uid', 'gid', 'mode', 'equals', 'biggerthan', 'smallerthan', 'target'}
        for __param in self.__data:
            if __param in __unsupported_bz2:
                self.__warn(__param)

    def __study_zip(self):
        '''Study the required checks for the zip archive type'''
        __unsupported_zip = {'target'}
        for __param in self.__data:
            if __param in __unsupported_zip:
                self.__warn(__param)

    def __study_lzma(self):
        '''Study the required checks for the lzma archive type'''
        # seems pretty hard to get xz/lzma archive size - maybe in another release
        __unsupported_lzma = {'uid', 'gid', 'mode', 'equals', 'biggerthan', 'smallerthan', 'target'}
        for __param in self.__data:
            if __param in __unsupported_lzma:
                self.__warn(__param)

    def __warn(self, __param):
        '''Warn the user that parameter is not supported by message in logging''' 
        logging.warning('{}: The required parameter {} is not supported by this type of archive. Ignoring it.'.format(self.__arcpath, __param))
