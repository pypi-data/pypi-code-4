#!/usr/bin/env python

"""
Unit tests for the veracity.vscript module.
"""

import unittest
from unittest.mock import patch, Mock

import os

from veracity import vscript
from veracity.vscript import VeracityScriptException

from veracity.test import TEST


class TestCommands(unittest.TestCase):  # pylint: disable=R0904
    """Tests for top-level Veracity commands."""  # pylint: disable=C0103

    def test_init_builds_invalid(self):
        """Verify an exception is raised when initializing builds with missing arguments."""
        self.assertRaises(VeracityScriptException, vscript.init_builds, '')

    def test_report_build_missing_args(self):
        """Verify an exception is raised when reporting builds with missing arguments."""
        self.assertRaises(VeracityScriptException, vscript.report_build, '')

    @patch('veracity.vscript.run', Mock(side_effect=VeracityScriptException("is not a valid")))
    def test_report_build_invalid_args(self):
        """Verify an exception is raised with invalid arguments."""
        self.assertRaises(ValueError, vscript.report_build, '')

    @patch('veracity.vscript.run', Mock(side_effect=VeracityScriptException("statusRec is null")))
    def test_report_build_no_config(self):
        """Verify an exception is raised when builds are not configured."""
        self.assertRaises(VeracityScriptException, vscript.report_build, '')

    @patch('veracity.vscript.run', Mock(side_effect=VeracityScriptException("is null")))
    def test_report_build_no_build(self):
        """Verify no exception occurs for unknown builds."""
        self.assertIsNone(vscript.report_build(''))


class TestRun(unittest.TestCase):  # pylint: disable=R0904
    """Tests for the Veracity scripting wrapper function."""  # pylint: disable=C0103

    def test_exception(self):
        """Verify a VeracityScriptException is raised for an invalid script path."""
        os.chdir(TEST)
        self.assertRaises(VeracityScriptException, vscript.run, 'not_a_script')

    def test_normal(self):
        """Verify text can be returned from vscript."""
        with patch.object(vscript, 'vscript') as _vscript:
            _result = Mock(stdout="test" if os.name == 'nt' else b"test")
            _vscript.bake = Mock(return_value=Mock(return_value=_result))
            self.assertEqual("test", vscript.run())


class TestParsing(unittest.TestCase):  # pylint: disable=R0904
    """Tests for parsing Veracity output."""  # pylint: disable=C0103

    def test_error(self):
        """Verify an unknown format cannot be parsed."""
        self.assertRaises(ValueError, list, vscript.parse("foo\nbar", 'unknown'))


if __name__ == '__main__':
    unittest.main()
