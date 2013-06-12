#!/usr/bin/python3 -u
"""
Setup script for PLIB3.GUI package
Copyright (C) 2008-2013 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information
"""

from plib.gui import __version__ as version

name = "plib3.gui"
description = "A simple Python GUI framework."

author = "Peter A. Donis"
author_email = "peterdonis@alum.mit.edu"

startline = 5
endspec = "The Zen of PLIB3"

dev_status = "Beta"

license = "GPLv2"

data_dirs = ["examples"]

classifiers = """
Environment :: Console
Environment :: MacOS X
Environment :: Win32 (MS Windows)
Environment :: X11 Applications :: GTK
Environment :: X11 Applications :: KDE
Environment :: X11 Applications :: Qt
Intended Audience :: Developers
Operating System :: MacOS :: MacOS X
Operating System :: Microsoft :: Windows
Operating System :: POSIX
Operating System :: POSIX :: Linux
Programming Language :: Python :: 2.7
Topic :: Software Development :: Libraries :: Python Modules
"""

requires = """
plib.stdlib (>=0.9.3)
"""

post_install = ["plib3-setup-{}.py".format(s) for s in ("gui-examples", "gui")]


if __name__ == '__main__':
    import sys
    import os
    from distutils.core import setup
    from setuputils import setup_vars
    setup(**setup_vars(globals()))
    if "install" in sys.argv:
        for scriptname in post_install:
            os.system(scriptname)
