#!/usr/bin/env python

"""
Unit tests for the veracity.poller module.
"""

import unittest

import os

from veracity.poller import Poller, run
from veracity.objects import Changeset, Branch
from veracity.common import Config

from veracity.test import TEST_REPO, REASON, FILES, log, temp_repo


def setUpModule():  # pylint: disable=C0103
    """Create a temporary repository for this module's tests.
    """
    global TEMP_REPO  # pylint: disable=W0601
    TEMP_REPO = temp_repo(__name__)


def tearDownModule():  # pylint: disable=C0103
    """Delete the temporary repository.
    """
    if TEMP_REPO:
        TEMP_REPO.delete()


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

    def test_build_name(self):
        """Verify the correct build name is returned."""
        name = Poller.name(1, 1000042, 'S', 'E', Changeset('abcde12345xxx'), Branch('dev', rev='abcde12345xxx')).split()
        self.assertIn("/", name[0])
        self.assertEqual(2, name[1].count(':'))
        self.assertEqual("abcde12345", name[2])


@unittest.skipUnless(TEST_REPO, REASON)  # pylint: disable=R0904
class TestRun(unittest.TestCase):  # pylint: disable=R0904
    """Tests for the main poller interface."""  # pylint: disable=C0103

    def setUp(self):
        del TEMP_REPO.builds

    def test_run_valid(self):
        """Verify a poller can be run."""
        self.assertTrue(run(Config(path=os.path.join(FILES, 'poller.cfg'), repos=[TEMP_REPO.name], series=['C'])))
        self.assertEqual(3, len(list(TEMP_REPO.builds)))
        self.assertTrue(run(Config(path=os.path.join(FILES, 'poller.cfg'), repos=[TEMP_REPO.name], series=['C'])))
        self.assertEqual(3, len(list(TEMP_REPO.builds)))

    def test_run_valid_with_rebuild(self):
        """Verify a poller can be run for a series that rebuilds."""
        self.assertTrue(run(Config(path=os.path.join(FILES, 'poller.cfg'), repos=[TEMP_REPO.name], series=['N'])))
        self.assertEqual(3, len(list(TEMP_REPO.builds)))
        self.assertTrue(run(Config(path=os.path.join(FILES, 'poller.cfg'), repos=[TEMP_REPO.name], series=['N'])))
        self.assertEqual(6, len(list(TEMP_REPO.builds)))

    def test_run_valid_test(self):
        """Verify a poller can be run in test mode."""
        self.assertTrue(run(Config(path=os.path.join(FILES, 'poller.cfg'), repos=[TEMP_REPO.name], series=['C'])))
        self.assertTrue(run(Config(path=os.path.join(FILES, 'poller.cfg'), repos=[TEMP_REPO.name], series=['C']), test=True))
        self.assertEqual(3, len(list(TEMP_REPO.builds)))
        del TEMP_REPO.builds
        self.assertTrue(run(Config(path=os.path.join(FILES, 'poller.cfg'), repos=[TEMP_REPO.name], series=['C']), test=True))
        self.assertEqual(0, len(list(TEMP_REPO.builds)))

    def test_run_invalid(self):
        """Verify a poller returns an error with no repository."""
        self.assertFalse(run(Config()))


if __name__ == '__main__':
    unittest.main()
