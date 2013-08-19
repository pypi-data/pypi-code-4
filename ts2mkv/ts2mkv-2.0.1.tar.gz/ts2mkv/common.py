import os
import sys
import glob

def modules_path():
    if sys.platform == 'win32' and os.path.dirname(__file__).endswith('library.zip\\ts2mkv'):
        #This module is called via an exe created by py2exe - not via python.exe or pythonw.exe
        return os.path.abspath(os.path.join(os.path.join(os.path.dirname(__file__), '..'), '..'))
    else:
        return os.path.dirname(__file__)

def config_files(ini_file_name):
    return [
        os.path.join(modules_path(), ini_file_name),
        os.path.normpath(os.path.expanduser('~/.ts2mkv/%s' % (ini_file_name))),
    ]

def expand_wildcards(arguments):
    all_files = []
    all_files.extend([arg for arg in arguments if os.path.exists(arg)])
    [all_files.extend(element) for element in [glob.glob(arg) for arg in arguments if not os.path.exists(arg)]]
    return list(set(all_files))
