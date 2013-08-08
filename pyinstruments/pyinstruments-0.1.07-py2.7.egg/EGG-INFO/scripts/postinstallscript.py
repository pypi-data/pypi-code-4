#!C:\Python27\python.exe
# -*- coding: utf-8 -*-

#import os
#import subprocess


import os
import sys
import shutil
#import curvefinder
import pkgutil
curvefinder = pkgutil.get_loader("curvefinder")
pyinstrumentsdb = pkgutil.get_loader("pyinstrumentsdb")

DESKTOP_FOLDER = get_special_folder_path("CSIDL_DESKTOPDIRECTORY")
CURVEFINDER_NAME = 'curvefinder.lnk'
PYINSTRUMENTSDB_NAME = 'pyinstrumentsdb.lnk'

create_shortcut(
        os.path.join(sys.prefix, 'python.exe'), # program
        'Description of the shortcut', # description
        CURVEFINDER_NAME, # filename
        os.path.join(curvefinder.filename, '__init__.py'), # parameters
        ''#, # workdir
        #os.path.join(os.path.dirname(my_package.__file__), 'favicon.ico'), # iconpath
    )
create_shortcut(
        os.path.join(sys.prefix, 'python.exe'), # program
        'Description of the shortcut', # description
        PYINSTRUMENTSDB_NAME, # filename
        os.path.join(pyinstrumentsdb.filename, '__init__.py'), # parameters
        ''#, # workdir
        #os.path.join(os.path.dirname(my_package.__file__), 'favicon.ico'), # iconpath
    )

# move shortcut from current directory to DESKTOP_FOLDER
shutil.move(os.path.join(os.getcwd(), CURVEFINDER_NAME),
            os.path.join(DESKTOP_FOLDER, CURVEFINDER_NAME))
shutil.move(os.path.join(os.getcwd(), PYINSTRUMENTSDB_NAME),
            os.path.join(DESKTOP_FOLDER, PYINSTRUMENTSDB_NAME))
# tell windows installer that we created another
# file which should be deleted on uninstallation
file_created(os.path.join(DESKTOP_FOLDER, CURVEFINDER_NAME))
file_created(os.path.join(DESKTOP_FOLDER, PYINSTRUMENTSDB_NAME))