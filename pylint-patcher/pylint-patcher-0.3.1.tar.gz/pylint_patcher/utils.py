"""
Utility functions
"""
import os
from logilab.common.modutils import file_from_modpath

def get_path_containing(file_or_module):
    """
    Returns the directory that contains the specified file or module.
    This is used to determine the location of the patchfile.
    """
    if os.path.exists(file_or_module):
        filepath = os.path.realpath(file_or_module)
        if os.path.isdir(filepath):
            return filepath
        else:
            return os.path.dirname(filepath)
    else:
        filepath = file_from_modpath(file_or_module.split('.'))
        return os.path.dirname(os.path.realpath(filepath))
