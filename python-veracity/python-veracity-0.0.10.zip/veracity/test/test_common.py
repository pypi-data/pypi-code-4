#!/usr/bin/env python

"""
Unit tests for the veracity.common module.
"""

import unittest
from unittest.mock import patch

import os
import logging
import tempfile

from veracity.common import Config, parse_config, find_config, configure_logging

from veracity.test import FILES


class TestModule(unittest.TestCase):  # pylint: disable=R0904
    """Tests for the common module."""  # pylint: disable=C0103

    @staticmethod
    def error(msg):
        """Error function to pass to the config parser."""
        raise Exception(msg)

    def test_find_config_found(self):
        """Verify a config can be found in this project."""
        self.assertTrue(os.path.isfile(find_config(FILES)))

    def test_find_config_found_from_parent(self):
        """Verify a config can be found by searching downwards."""
        self.assertTrue(os.path.isfile(find_config(os.path.dirname(FILES), walk=True)))

    def test_find_config_not_found(self):
        """Verify None is returned when no config is found."""
        self.assertIsNone(find_config(tempfile.mkdtemp(), walk=True))

    def test_find_config_not_found_no_walk(self):
        """Verify None is returned when no searching is enabled."""
        self.assertIsNone(find_config(os.path.dirname(FILES)))

    def test_parse_config_valid(self):
        """Verify a config can be parsed."""
        config = parse_config(os.path.join(FILES, 'setup.cfg'), False, self.error)
        self.assertEqual(['python-veracity-test'], config.repos)

    def test_parse_config_found(self):
        """Verify a config can be found and parsed."""
        os.chdir(FILES)
        config = parse_config(None, True, self.error)
        self.assertEqual(['python-veracity-test'], config.repos)

    def test_parse_config_invalid(self):
        """Verify an error occurs when no config is found."""
        self.assertRaises(Exception, parse_config, tempfile.gettempdir(), True, self.error)

    def test_configure_logging(self):
        """Verify the default logging is set."""
        with patch('logging.basicConfig') as _basicConfig:
            configure_logging()
        _basicConfig.assert_called_with(level=logging.INFO)

    def test_configure_logging_1(self):
        """Verify the logging level 1 is set."""
        with patch('logging.basicConfig') as _basicConfig:
            configure_logging(1)
        _basicConfig.assert_called_with(level=logging.DEBUG)

    def test_configure_logging_2(self):
        """Verify the logging level 2 is set."""
        with patch('logging.basicConfig') as _basicConfig:
            configure_logging(2)
        _basicConfig.assert_called_with(level=logging.DEBUG)

    def test_configure_logging_3(self):
        """Verify the logging level 3 is set."""
        with patch('logging.basicConfig') as _basicConfig:
            configure_logging(3)
        _basicConfig.assert_called_with(level=logging.DEBUG)


class TestConfig(unittest.TestCase):  # pylint: disable=R0904
    """Tests for the Config class."""  # pylint: disable=C0103

    @classmethod
    def setUpClass(cls):
        cls.config = Config(os.path.join(FILES, 'setup.cfg'))

    def test_copy(self):
        """Verify a configuration can be copied."""
        config1 = Config()
        config2 = config1.copy()
        config3 = config1
        config1.updated = True
        self.assertEqual(config1.updated, config3.updated)
        self.assertNotEqual(config1.updated, config2.updated)

    def test_override(self):
        """Verify a configuration options can be overridden."""
        config = Config(os.path.join(FILES, 'setup.cfg'),
                        repos=['r1', 'r2'], series=['s1', 's2'], envs=['e1', 'e2'])
        self.assertEqual(['r1', 'r2'], config.repos)
        self.assertEqual(['s1', 's2'], config.series)
        self.assertEqual(['e1', 'e2'], config.environments)

    def test_no_override(self):
        """Verify a configuration options cannot be overridden with empty items."""
        config = Config(os.path.join(FILES, 'setup.cfg'),
                        repos=[], series=[], envs=[])
        self.assertEqual(['python-veracity-test'], config.repos)
        self.assertEqual(['C', 'N'], config.series)
        self.assertEqual(['L', 'M', 'W'], config.environments)
        self.assertEqual('abc', config.virtualenv)

    def test_starts(self):
        """Verify starts can be read from a config."""
        self.assertEqual(['Q', 'Q2'], self.config.starts)

    def test_starts_default(self):
        """Verify default starts can be read from an empty config."""
        config = Config()
        self.assertEqual(['Q'], config.starts)

    def test_ends(self):
        """Verify sends can be read from a config."""
        self.assertEqual(['BF', 'CF', 'D', 'TF', 'UF'], self.config.ends)

    def test_fails(self):
        """Verify fails can be read from a config."""
        self.assertEqual(['BF', 'CF', 'TF', 'UF'], self.config.fails)

    def test_next_valid(self):
        """Verify a valid state can be entered."""
        self.assertEqual('B', self.config.next('UP'))

    def test_next_invalid(self):
        """Verify the absence of a next state raises an exception."""
        self.assertRaises(ValueError, self.config.next, 'FAKE')

    def test_fail(self):
        """Verify a a state can be failed."""
        self.assertEqual('UF', self.config.fail('U'))

    def test_fail_invalid(self):
        """Verify the absence of a fail state raises an exception."""
        self.assertRaises(ValueError, self.config.fail, 'FAKE')

    def test_exit(self):
        """Verify a state can be exited."""
        self.assertEqual('UP', self.config.exit('U'))

    def test_exit_stay(self):
        """Verify a state does not need an exit."""
        self.assertEqual('FAKE', self.config.exit('FAKE'))

    @patch('os.name', 'posix')
    def test_get_poll_posix(self):
        """Verify poll operations can be retrieved."""
        self.assertEqual(([], '[ $( date "+%H" ) = 0 ]', '', 'Q', 1800),
                         self.config.get_poll('N'))

    @patch('os.name', 'nt')
    def test_get_poll_nt(self):
        """Verify poll operations can be retrieved."""
        self.assertEqual(([], 'nt command', '', 'Q', 1800),
                         self.config.get_poll('N'))

    def test_get_poll_with_branches(self):
        """Verify poll operations can be retrieved with branches."""
        self.assertEqual((['master', 'develop', 'release-1.0'], '', '', 'Q', 0),
                         self.config.get_poll('C', all_branches=['release-1.0']))

    def test_get_build(self):
        """Verify build operations can be retrieved."""
        self.assertEqual(('test_path', 'test'), self.config.get_build('T'))


if __name__ == '__main__':
    unittest.main()
