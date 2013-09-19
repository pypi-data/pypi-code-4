__copyright__ = """ Copyright (c) 2012-2013 Torsten Schmits

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

import os

from tek.config import (Configurations, PathConfigOption, DictConfigOption,
                        ListConfigOption, BoolConfigOption,
                        FileSizeConfigOption, standard_config_files)

def reset_config():
    Configurations.register_files('sharehoster',
                                  *standard_config_files('sharehoster'))
    Configurations.register_config('sharehoster', 'common',
                                   out_dir=PathConfigOption(os.getcwd()),
                                   link_checker_url=None,
                                   progress_update_interval=1)
    Configurations.register_config('sharehoster', 'rapidshare', login=None,
                                   password=None)
    Configurations.register_config('sharehoster', 'netload',
                                   cookies=DictConfigOption())
    Configurations.register_config('sharehoster', 'uploaded',
                                   cookies=DictConfigOption())
    Configurations.register_config('sharehoster', 'zevera',
                                   cookies=DictConfigOption(),
                                   providers=ListConfigOption())
    min_size_help = 'Minimum of the file size sum on a single page'
    min_size = FileSizeConfigOption(short='s', help=min_size_help)
    Configurations.register_config('sharehoster', 'search', web_url=None,
                                match_url=ListConfigOption([], short='m'),
                                match_url_all=BoolConfigOption(False, short='M'),
                                terms=ListConfigOption(positional=True),
                                min_size=min_size,
                                providers=ListConfigOption())
    Configurations.register_config('sharehoster', 'shget',
                                   urls=ListConfigOption(positional=True))

reset_config()
