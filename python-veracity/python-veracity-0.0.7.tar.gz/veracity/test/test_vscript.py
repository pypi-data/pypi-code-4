#!/usr/bin/env python

"""
Unit tests for the veracity.vscript module.
"""

import unittest
import os

from veracity import vscript

from veracity.test import TEST


class TestCommands(unittest.TestCase):  # pylint: disable=R0904
    """Tests for top-level Veracity commands."""  # pylint: disable=C0103

    def test_init_builds_invalid(self):
        """Verify an exception is raised when initializing builds with missing arguments."""
        self.assertRaises(vscript.VeracityScriptException, vscript.init_builds, '')

    def test_report_build_missing_args(self):
        """Verify an exception is raised when reporting builds with missing arguments."""
        self.assertRaises(vscript.VeracityScriptException, vscript.report_build, '')


class TestRun(unittest.TestCase):  # pylint: disable=R0904
    """Tests for the Veracity scripting wrapper function."""  # pylint: disable=C0103

    def test_exception(self):
        """Verify a VeracityScriptException is raised for an invalid script path."""
        os.chdir(TEST)
        self.assertRaises(vscript.VeracityScriptException, vscript.run, 'not_a_script')


class TestParsing(unittest.TestCase):  # pylint: disable=R0904
    """Tests for parsing Veracity output."""  # pylint: disable=C0103

    def test_error(self):
        """Verify an unknown format cannot be parsed."""
        self.assertRaises(ValueError, list, vscript.parse("foo\nbar", 'unknown'))


if __name__ == '__main__':
    unittest.main()
