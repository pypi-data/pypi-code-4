#!/usr/bin/python3 -u
"""
Setup script for PLIB3.STDLIB package
Copyright (C) 2008-2013 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information
"""

from plib.stdlib import __version__ as version

name = "plib3.stdlib"
description = "Useful packages and modules to extend the Python 3 standard library."

author = "Peter A. Donis"
author_email = "peterdonis@alum.mit.edu"

startline = 5
endspec = "The Zen of PLIB3"

dev_status = "Beta"

license = "GPLv2"

ext_names = ['plib.stdlib.extensions._extensions']
ext_srcdir = "src"

classifiers = """
Environment :: Console
Environment :: MacOS X
Environment :: Win32 (MS Windows)
Intended Audience :: Developers
Operating System :: MacOS :: MacOS X
Operating System :: Microsoft :: Windows
Operating System :: POSIX
Operating System :: POSIX :: Linux
Topic :: Software Development :: Libraries :: Python Modules
"""


if __name__ == '__main__':
    from distutils.core import setup
    from setuputils import setup_vars
    setup(**setup_vars(globals()))
