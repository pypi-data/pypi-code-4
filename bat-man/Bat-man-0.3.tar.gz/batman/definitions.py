import sys
import os
import logging

logging.basicConfig(level=logging.DEBUG)

VERSION = "0.3"
if getattr(sys, "frozen", False):
    CURRENT_PATH = os.path.join(os.path.dirname(os.path.realpath(sys.executable)), "batman")
else:
    CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
    
WINDOWS = sys.platform.startswith("win")

def path_with(*args):
    return os.path.join(CURRENT_PATH, *args)

# Prepare for user data
try:
    os.mkdir(os.path.expanduser("~/.batman"))
except OSError: # OSError is raised if the directory already exists.
    pass

def get_user_data_folder():
    if not WINDOWS:
        return os.path.expanduser("~/.batman")

def get_user_data_folder_with(*args):
    return os.path.join(get_user_data_folder(), *args)

# OPTIONS is defined at the options.py file. Yes, bad, but it avoids circular
# dependencies.

