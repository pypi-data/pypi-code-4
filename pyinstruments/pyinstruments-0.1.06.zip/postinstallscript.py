#! python
# -*- coding: utf-8 -*-

import os
import subprocess


import os
import sys
import shutil
import curvefinder

DESKTOP_FOLDER = get_special_folder_path("CSIDL_DESKTOPDIRECTORY")
NAME = 'curvefinder_lnk.py'

create_shortcut(
    os.path.join(sys.prefix, 'pythonw.exe'), # program
    'Description of the shortcut', # description
    NAME, # filename
    curvefinder.__file__, # parameters
    '' # workdir
#    os.path.join(os.path.dirname(curvefinder.__file__), 'favicon.ico'), # iconpath
)
# move shortcut from current directory to DESKTOP_FOLDER
shutil.move(os.path.join(os.getcwd(), NAME),
            os.path.join(DESKTOP_FOLDER, NAME))
# tell windows installer that we created another
# file which should be deleted on uninstallation
file_created(os.path.join(DESKTOP_FOLDER, NAME))

    # This will be run on uninstallation. Nothing to do.























def set_environment_variable_on_windows(name, value):
    subprocess.call(['setx', name, value])
    os.environ[name] = value

def desktop_folder():
    #import win32com.client
    #oShell = win32com.client.Dispatch("Wscript.Shell")
    return os.path.join(os.environ['HOMEPATH'], 'Desktop')

def install_dependancies():
    # Call parent
    subprocess.call(['pip', 'install', 'django'])
    subprocess.call(['python', 'setup_datastore.py', 'install'])
    set_environment_variable_on_windows('DJANGO_SETTINGS_MODULE', 'datastore.settings')
    subprocess.call(['pip', 'install', 'django-model-utils'])
    subprocess.call(['pip', 'install', 'django-utils'])

def create_all_shortcuts():
    #try:
    #    import win32com
    #except ImportError:
    #    print """won t add desktop icons because this computer seems not to be 
    #    under windows"""
    #else:
        desktop = desktop_folder()
        with open(os.path.join(desktop, 'curvefinder_shortcut.py'), 'w') as shortcut:
             shortcut.write("""
from curvefinder import gui
from guidata import qapplication as __qapplication
_APP = __qapplication()
GUI = gui()
_APP.exec_()
""")
            
        with open(os.path.join(desktop, 'pyinstrumentsdb_shortcut.py'), 'w') as shortcut:
             shortcut.write("""
from pyinstrumentsdb import gui
from guidata import qapplication as __qapplication
_APP = __qapplication()
GUI = gui()
_APP.exec_()
""")
             
