#!/usr/bin/env python

"""
Unit tests for the veracity.poller module.
"""

import unittest

import os

from veracity.poller import Poller, run
from veracity.common import Config

from veracity.test import TEST_REPO, REASON, FILES, log


class TestPoller(unittest.TestCase):  # pylint: disable=R0904
    """Tests for the Poller class."""  # pylint: disable=C0103

    def test_from_config(self):
        """Verify a poller can be created from a config."""
        poller1 = Poller(TEST_REPO.name, Config(series=['N']))
        poller2 = Poller(TEST_REPO.name, Config(series=['N']))
        poller3 = Poller(TEST_REPO.name, Config(series=['C']))
        log(poller1, poller2, poller3)
        self.assertEqual(poller1, poller2)
        self.assertNotEqual(poller1, poller3)
        self.assertNotEqual(poller1, TEST_REPO.name)


@unittest.skipUnless(TEST_REPO, REASON)  # pylint: disable=R0904
class TestRun(unittest.TestCase):  # pylint: disable=R0904
    """Tests for the main poller interface."""  # pylint: disable=C0103

    def test_run_valid(self):
        """Verify a poller can be run."""
        del TEST_REPO.builds
        self.assertTrue(run(Config(path=os.path.join(FILES, 'poller.cfg'))))
        self.assertEqual(3, len(list(TEST_REPO.builds)))
        self.assertTrue(run(Config(path=os.path.join(FILES, 'poller.cfg'))))
        self.assertEqual(3, len(list(TEST_REPO.builds)))

    def test_run_valid_test(self):
        """Verify a poller can be run in test mode."""
        self.assertTrue(run(Config(path=os.path.join(FILES, 'poller.cfg'))))
        self.assertTrue(run(Config(path=os.path.join(FILES, 'poller.cfg')), test=True))
        self.assertEqual(3, len(list(TEST_REPO.builds)))
        del TEST_REPO.builds
        self.assertTrue(run(Config(path=os.path.join(FILES, 'poller.cfg')), test=True))
        self.assertEqual(0, len(list(TEST_REPO.builds)))

    def test_run_invalid(self):
        """Verify a poller returns an error with no repository."""
        self.assertFalse(run(Config()))


if __name__ == '__main__':
    unittest.main()
