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

# The application main
'''The application main'''

import sys

from brebis.checkbackups.checkbackups import CheckBackups
from brebis.cliparse import CliParse
from brebis.configurations import Configurations
from brebis.listtype import ListType

class Main(object):
    '''The main class'''

    def __init__(self):
        '''The constructor of the Main class.'''
        self.__main()

    def __main(self):
        '''The main for the Main class'''
        __options = CliParse().options
        # no list generation mode, check backups 
        if not __options.genlist and not __options.genfull:
            __confs = Configurations(__options.confpath)
            CheckBackups(__confs.configs, __options)
        else:
        # Analyze the type of the list to produce
            ListType(__options)
