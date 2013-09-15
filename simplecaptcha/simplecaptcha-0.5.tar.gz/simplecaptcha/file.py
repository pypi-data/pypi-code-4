""" Captcha.File

Utilities for finding and picking random files from our 'data' directory

SimpleCaptcha Package
Forked from PyCAPTCHA Copyright (C) 2004 Micah Dowty <micah@navi.cx>
"""
import os
import random

# Determine the data directory. This can be overridden after import-time if
# needed.
data_dir = os.path.join(os.path.split(os.path.abspath(__file__))[0], "data")


class RandomFileFactory(object):
    """Given a list of files and/or directories, this picks a random file.
    Directories are searched for files matching any of a list of extensions.
    Files are relative to our data directory plus a subclass-specified base
    path.  """
    extensions = []
    base_path = "."

    def __init__(self, *file_list):
        self.file_list = file_list
        self._full_paths = None

    def _check_extension(self, name):
        """Check the file against our given list of extensions"""
        for ext in self.extensions:
            if name.endswith(ext):
                return True
        return False

    def _find_full_paths(self):
        """From our given file list, find a list of full paths to files"""
        paths = []
        for name in self.file_list:
            path = os.path.join(data_dir, self.base_path, name)
            if os.path.isdir(path):
                for content in os.listdir(path):
                    if self._check_extension(content):
                        paths.append(os.path.join(path, content))
            else:
                paths.append(path)
        return paths

    def pick(self):
        if self._full_paths is None:
            self._full_paths = self._find_full_paths()
        return random.choice(self._full_paths)
