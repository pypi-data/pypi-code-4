__copyright__ = """ Copyright (c) 2009-2011 Torsten Schmits

This file is part of tek-utils. tek-utils is free software;
you can redistribute it and/or modify it under the terms of the GNU General
Public License version 2, as published by the Free Software Foundation.

tek-utils is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
details.

You should have received a copy of the GNU General Public License along with
this program; if not, write to the Free Software Foundation, Inc., 59 Temple
Place, Suite 330, Boston, MA  02111-1307  USA

"""

from os import path
from sys import stdin

from tek.config import Configurations

def reset_config(register_files=True, reset_parent=False):
    Configurations.clear()
    interactive = stdin.isatty()
    tekutils_config_dir = '/etc/tek-utils'
    tekutils_config_files = ((path.join(tekutils_config_dir, 'tek-utils.conf'),
                              '~/.config/tek-utils.conf') if
                             register_files else [])
    Configurations.register_files('tekutils', *tekutils_config_files)
    Configurations.register_config('tekutils', 'global',
                                   interactive=interactive)

reset_config()
