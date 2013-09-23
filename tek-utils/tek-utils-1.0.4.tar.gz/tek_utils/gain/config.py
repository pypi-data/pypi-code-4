__copyright__ = """ Copyright (c) 2011 Torsten Schmits

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation; either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, see <http://www.gnu.org/licenses/>.
"""

from tek.config import Configurations

try:
    from tek_utils.config import reset_config as tu_reset_config
    has_parent = True
except ImportError:
    has_parent = False

def reset_config(register_files=True, reset_parent=False):
    if has_parent and reset_parent:
        tu_reset_config(register_files=register_files)
    Configurations.register_config('tekutils', 'music',
                                   collection_dir='/home/media/music',
                                   gain_value='0')
reset_config()
