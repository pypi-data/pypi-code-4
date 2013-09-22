"""Perform diff operations"""
import sys
import os
import tempfile
import shutil
import subprocess
import fileinput

import pylint_patcher.patcher
from . import utils

_DISABLE_MSGS = "# pylint: disable=" # pylint: disable=bad-option-value

class Differ(object):
    """
    Perform diff operations, and insert "Pylint disable" pragmas.
    Usage:
        # First set up the differ. This creates:
        #    original_path: a temporary copy of the original target
        #    patched_path:  a temporary copy of the target with any
        #                   existing patchfile applied

        diff = Differ()
        diff.setup(file_or_module)

        # Now add a new "Pylint disable" pragma to a file in patched_path:

        diff.add_disable_pragma(filepath, fileline, message_code)

        # Now create an updated patchfile:

        diff.diff()

        # Finally, clean up the temporary directories:

        diff.cleanup()
"""
    def __init__(self):
        self._target = None
        self._source_path = None
        self._temp_path = tempfile.mkdtemp(prefix="pylint_")
        self._temp_original_dirname = "original"
        self._temp_original_path = os.path.join(self._temp_path,
                                                self._temp_original_dirname)
        self._temp_patched_dirname = "patched"
        self._temp_patched_path = os.path.join(self._temp_path,
                                               self._temp_patched_dirname)

    def setup(self, file_or_module):
        """
        Create two temporary directories, copy the source into them,
        and apply any existing patches to the "patched" temp directory.
        """
        self.cleanup()
        self._target = file_or_module
        self._source_path = utils.get_path_containing(file_or_module)
        shutil.copytree(self._source_path, self._temp_original_path)
        shutil.copytree(self._source_path, self._temp_patched_path)
        pylint_patcher.patcher.Patcher(self._temp_patched_path).patch()

    def diff(self):
        """Create a patchfile from the "patched" temporary copy's changes."""
        patchfile = os.path.join(self._source_path,
                                 pylint_patcher.PATCHFILENAME)

        cwd = os.getcwd()
        os.chdir(self._temp_path)
        try:
            cmd = ["diff", "--unified", "--recursive",
                   "--exclude=%s" % pylint_patcher.PATCHFILENAME,
                   self._temp_original_dirname,
                   self._temp_patched_dirname]
            returncode = subprocess.call(cmd, stdout=open(patchfile, "w"))
        finally:
            os.chdir(cwd)

        self._remove_timestamps(patchfile)
        if returncode > 1:
            raise ValueError("diff command returned code %d" % returncode)

    def add_disable_pragma(self, filepath, fileline, message_code):
        """
        Add a "Pylint disable" pragma to the specified file line of the
        "patched" temporary copy.
        """
        # Normalise the filepath and check that it's valid
        filepath = os.path.normpath(filepath)
        if not filepath.startswith(self._source_path):
            raise ValueError("File %s is not inside %s" %
                             (filepath, self._source_path))

        source_file = os.path.relpath(filepath, self._source_path)
        temp_filepath = os.path.join(self._temp_patched_path, source_file)

        for line in fileinput.input(temp_filepath, inplace=True):
            if fileinput.lineno() == fileline:
                line = self._insert_comment(line, message_code)
            sys.stdout.write(line)
        fileinput.close()

    @staticmethod
    def _insert_comment(line, message_code):
        """ Add a "Pylint disable" comment to the line """
        if _DISABLE_MSGS in line:
            insert_pos = line.rfind(_DISABLE_MSGS) + len(_DISABLE_MSGS)
            comment = message_code + ","
        else:
            insert_pos = len(line.rstrip("\r\n"))
            comment = " " + _DISABLE_MSGS + message_code

        return line[:insert_pos] + comment + line[insert_pos:]

    def _remove_timestamps(self, patchfile):
        """Remove all timestamps from the patchfile headers"""
        pattern1 = "--- %s/" % self._temp_original_dirname
        pattern2 = "+++ %s/" % self._temp_patched_dirname

        lines = open(patchfile).readlines()
        with open(patchfile, "w") as output:
            for line in lines:
                split = line.split("\t")
                if len(split) == 2:
                    if (split[0].startswith(pattern1) or
                        split[0].startswith(pattern2)):
                        line = split[0] + "\n"

                output.write(line)

    def cleanup(self):
        """Remove all temporary files & directories"""
        if os.path.exists(self._temp_path):
            shutil.rmtree(self._temp_path)
