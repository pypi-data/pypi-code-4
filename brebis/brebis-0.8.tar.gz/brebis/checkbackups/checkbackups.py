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

# Check the given backups
'''Check the given backups'''

import logging
from tarfile import is_tarfile
from zipfile import is_zipfile

from brebis.archiveinfomsg import ArchiveInfoMsg
from brebis.checkbackups.checktar import CheckTar
from brebis.checkbackups.checkgzip import CheckGzip
from brebis.checkbackups.checkbzip2 import CheckBzip2
from brebis.checkbackups.checklzma import CheckLzma
from brebis.checkbackups.checkzip import CheckZip
from brebis.checkbackups.checktree import CheckTree

class CheckBackups(object):
    '''The backup checker class'''

    def __init__(self, __confs, __options):
        '''The constructor for the Checkbackups class.

        __confs -- the different configurations of the backups
        __options -- global options from the command line

        '''
        self.__main(__confs, __options)

    def __main(self, __confs, __options):
        '''Main for CheckBackups'''
        __cfgsets = __confs.values()
        for __cfgvalues in __cfgsets:
            # check a file tree
            if __cfgvalues['type'] == 'tree':
                __bck = CheckTree(__cfgvalues, __options)
            # check a tar file, by name
            elif __cfgvalues['type'] == 'archive' and (__cfgvalues['path'].lower().endswith('.tar') \
                or __cfgvalues['path'].lower().endswith('.tar.gz') \
                or __cfgvalues['path'].lower().endswith('.tar.bz2') \
                or __cfgvalues['path'].lower().endswith('.tar.xz') \
                or __cfgvalues['path'].lower().endswith('.tgz') \
                or __cfgvalues['path'].lower().endswith('.tbz') \
                or __cfgvalues['path'].lower().endswith('.tbz2')):
                __bck = CheckTar(__cfgvalues, __options)
            # check a gzip file, by name
            elif __cfgvalues['type'] == 'archive' and __cfgvalues['path'].lower().endswith('.gz'):
                __bck = CheckGzip(__cfgvalues, __options)
            # check a bzip2 file, by name
            elif __cfgvalues['type'] == 'archive' and __cfgvalues['path'].lower().endswith('.bz2'):
                __bck = CheckBzip2(__cfgvalues, __options)
            # check a xz file, by name
            elif __cfgvalues['type'] == 'archive' and __cfgvalues['path'].lower().endswith('.xz'):
                __bck = CheckLzma(__cfgvalues, __options)
            # check a zip file, by name
            elif __cfgvalues['type'] == 'archive' and __cfgvalues['path'].lower().endswith('.zip'):
                __bck = CheckZip(__cfgvalues, __options)
            ArchiveInfoMsg(__bck, __cfgvalues)
