#!/usr/bin/env python3

# Copyright (C) 2013 LiuLang <gsushzhsosgsu@gmail.com>

# Use of this source code is governed by GPLv3 license that can be found
# in http://www.gnu.org/licenses/gpl-3.0.html

# Distutils script for python3-xlib

from distutils.core import setup

import keybinder

if __name__ == '__main__':
    setup(
        name = 'python3-keybinder',
        version = keybinder.__version_string__,
        description = "Python3 Keybinding Library for X",
        url = 'https://github.com/LiuLang/python3-keybinder',
        license = 'http://www.gnu.org/licenses/gpl-3.0.html',

        author = 'LiuLang',
        author_email = 'gsushzhsosgsu@gmail.com',

        long_description = '''\
python3-keybinder uses python3-Xlib to bind global keyboard shortcuts.
It runs on almost all desktop environments and window managers on Linux
Desktop.
''',
        packages = ['keybinder', ],
        )
