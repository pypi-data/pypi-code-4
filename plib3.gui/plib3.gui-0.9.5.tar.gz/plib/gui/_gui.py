#!/usr/bin/env python3
"""
Internal Module _GUI
Sub-Package GUI of Package PLIB3 -- Python GUI Framework
Copyright (C) 2008-2013 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the code to determine what GUI toolkit
should be used. It is for internal use by the other GUI
modules; user applications should not need to import it
since the GUI sub-package itself contains the gui_toolkit
variable in its namespace.
"""

import sys
import os

from plib.gui.defs import GUI_WX, GUI_KDE4, GUI_QT4, GUI_PYSIDE
from plib.gui._setup import *

# This variable is provided so that if you want to test your own toolkit
# that's not in the supported list, you can still use the other facilities;
# you just need to import this module and set this variable to True before
# importing plib.gui.main. However, note that if you do this, *none* of the
# standard GUI widget classes will be available unless you add them yourself;
# you can do this by setting attributes on this module before importing
# plib.gui.main, or by constructing all your widgets "by hand". The former
# technique has the advantage of allowing you to use PLIB3.GUI's other
# built-in facilities, but it requires you to provide classes with all the
# appropriate names yourself (they can be dummy classes if you won't use
# them, but they must be there). For example:
#
# from plib.gui import _gui
# _gui.gui_test = True
# _gui.PApplication = PMyApplication # assuming this was defined earlier
# _gui.PTopWindow = PMyTopWindow
# ... etc. for all other GUI widget classes
#
# Once you do this, you can use the rest of PLIB3.GUI normally, including
# classes like PAutoPanel that allow you to define GUI specs declaratively.
gui_test = False

# GUI toolkit determination -- this has to be here to avoid circular imports
# among the various GUI modules
gui_toolkit = 0

# If environment variable present and correct, it determines the toolkit
env_toolkit_name = os.getenv("GUI_TOOLKIT")
if env_toolkit_name is not None:
    # Hack to allow env var to be either numeric value or name of the constant
    try:
        gui_toolkit = int(env_toolkit_name)
    except ValueError:
        for name in dir(sys.modules[__name__]):
            if name == env_toolkit_name:
                gui_toolkit = getattr(sys.modules[__name__], name)
                break
        del name

# Clean up namespace
del env_toolkit_name

# If toolkit not set above, detect desktop environment
if gui_toolkit == 0:
    desktop_session = os.getenv('DESKTOP_SESSION')
    window_mgr = os.getenv('WINDOWMANAGER')
    
    # check KDE/Qt first
    if KDE4_PRESENT or QT4_PRESENT or PYSIDE_PRESENT:
        kde_session = 'KDE_FULL_SESSION' in os.environ
        kde_desktop = (desktop_session in ('kde', 'trinity'))
        kde_winmgr = isinstance(window_mgr, str) and \
            (window_mgr.find('kde') > -1)
        # TODO: check if kdeinit (kde root process) and kwin (kde
        # window mgr) are running
        
        # if KDE is running, default to KDE if PyKDE is present,
        # otherwise Qt; but make sure the versions match
        if kde_session or kde_desktop or kde_winmgr:
            if os.getenv('KDE_SESSION_VERSION') == '4':
                if KDE4_PRESENT:
                    gui_toolkit = GUI_KDE4
                elif QT4_PRESENT:
                    gui_toolkit = GUI_QT4
                elif PYSIDE_PRESENT:
                    # This is the last choice because it appears to be less
                    # "canonical" than PyQt4
                    gui_toolkit = GUI_PYSIDE
        
        # clean up namespace
        del kde_session, kde_desktop, kde_winmgr
    
    # check Qt 4 if none of the above worked
    if (gui_toolkit == 0) and QT4_PRESENT:
        gui_toolkit = GUI_QT4
    
    # check PySide if none of the above worked
    if (gui_toolkit == 0) and PYSIDE_PRESENT:
        gui_toolkit = GUI_PYSIDE
    
    # default to wxWidgets if present
    if (gui_toolkit == 0) and WX_PRESENT:
        gui_toolkit = GUI_WX
    
    # clean up namespace
    del desktop_session, window_mgr

del sys, os
