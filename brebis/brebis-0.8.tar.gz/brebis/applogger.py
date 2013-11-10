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

# Application logger
'''Application logger'''

import logging
import sys

class AppLogger(object):
    '''The application logger'''

    def __init__(self, __logfile):
        '''The constructor for the AppLogger class.

        Keyword arguments:
        __logfile -- the path of the log

        '''
        try:
            logging.basicConfig(filename=__logfile,
                level=logging.WARNING, filemode='w')
        except (IOError,OSError) as __msg:
            print('Brebis output file could not be created: {}'.format(__msg))
            sys.exit(1)
