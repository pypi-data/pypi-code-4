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

# Check the hash of the list of files by comparing it to the expected value
'''Check the hash of the list of files by comparing it to the expected value'''

import sys

from brebis.checkhashes import get_hash

class CheckFileList(object):
    '''Check the hash of the list of files by comparing it to the expected value'''

    def __init__(self, __bckconf):
        '''The constructor of the CheckFileList class.'''
        self.__main(__bckconf)

    def __main(self, __bckconf):
        '''The main for the CheckFileList class'''
        if 'sha512' in __bckconf and __bckconf['sha512'] != None:
            __hashtype = 'sha512'
            with open(__bckconf['files_list'], 'rb') as __conf:
                __realhash = get_hash(__conf, __hashtype)
            if __realhash != __bckconf['sha512']:
                print('The list of files {} should have a {} hash sum of {}. Current value: {}'.format(__bckconf['files_list'], __hashtype, __bckconf['sha512'], __realhash))
                sys.exit(1)
