#!/usr/bin/env python3
"""
SETUP-GUI script for Package PLIB3
Copyright (C) 2008-2013 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This script determines what GUI toolkits are present on the system,
and writes a _setup.py module to the plib.gui directory that defines
appropriate constants. This module is then loaded by the main gui module
to determine which toolkits are available for use. The script should be
run after the sub-packages for PLIB3 are installed, since it uses some of
them.

Note that this script should only need to be run on initial installation
of PLIB3 or when toolkit packages are installed or uninstalled.
"""

import os

from plib.stdlib import postinstall

import plib.gui

print("Determining which GUI toolkits are available...")

# Check which GUI toolkits are available

WX_PRESENT = False
try:
    import wx
except ImportError:
    pass
else:
    WX_PRESENT = True

QT4_PRESENT = False
try:
    from PyQt4 import Qt
except ImportError:
    pass
else:
    QT4_PRESENT = True

KDE4_PRESENT = False
try:
    from PyKDE4 import kdecore
except ImportError:
    pass
except RuntimeError as e:
    if 'PyQt4.QtCore' in str(e):
        # This will happen if Qt 3 and Qt 4 are both present
        KDE4_PRESENT = True
else:
    KDE4_PRESENT = True

PYSIDE_PRESENT = False
try:
    from PySide import QtCore
except ImportError:
    pass
else:
    PYSIDE_PRESENT = True

module_vars = [
    'WX_PRESENT', 'QT4_PRESENT', 'KDE4_PRESENT', 'PYSIDE_PRESENT'
]
outpath = plib.gui.__path__[0]
outfilename = "_setup.py"
startlines = [
    "{}{}".format(s, os.linesep) for s in [
        "#!/usr/bin/env python3",
        "# SETUP -- PLIB3.GUI Toolkit Setup Module",
        "# *** This module is automatically generated; do not edit. ***",
        ""
    ]
]

postinstall.write_setup_file(__name__, module_vars, outpath, outfilename, startlines)

print("PLIB3 GUI setup done!")
