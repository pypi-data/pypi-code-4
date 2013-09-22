"""Perform patch/unpatch operations"""
import os
import subprocess

import pylint_patcher
from . import utils

class Patcher(object):
    """Perform patch/unpatch operations"""
    def __init__(self, file_or_module):
        """
        file_or_module is name of the target directory/file/module
        to be patched.
        """
        self._path = utils.get_path_containing(file_or_module)

    def patch(self, reverse=False):
        """
        Applies the patchfile.
        Returns False if the patchfile doesn't exist.
        """
        patchfile = os.path.join(self._path, pylint_patcher.PATCHFILENAME)
        if not os.path.exists(patchfile):
            return False

        cmd = ["patch", "--unified", "--posix", "--strip=1",
               "--quiet", "--force",
               "--reject-file=-", "--no-backup-if-mismatch",
               "--directory=%s" % self._path,
               "--input=%s" % patchfile]
        if reverse:
            cmd.append("--reverse")
        returncode = subprocess.call(cmd)
        if returncode > 1:
            raise ValueError("patch command returned code %d" % returncode)
        return True

    def unpatch(self):
        """
        Reverts the patchfile.
        Returns False if the patchfile doesn't exist.
        """
        return self.patch(reverse=True)
