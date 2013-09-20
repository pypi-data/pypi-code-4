#!/usr/bin/env python

"""
Unit tests for the veracity.tracking module.
"""

import unittest

from veracity.tracking import run

from veracity.test import TEST_REPO, REASON, temp_repo


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


@unittest.skipUnless(TEST_REPO, REASON)  # pylint: disable=R0904
class TestRun(unittest.TestCase):  # pylint: disable=R0904
    """Tests for the main tracking interface."""  # pylint: disable=C0103

    def test_run_initialize(self):
        """Verify a default build configuration can be initialized."""
        self.assertTrue(run(TEMP_REPO.name, initialize=True))

    def test_run_initialize_invalid_repo(self):
        """Verify an error is returned when initializing an invalid repo."""
        self.assertFalse(run('_invalid_repo_', initialize=True))

    def test_run_delete_build_invalid(self):
        """Verify deleting an unknown build request returns an error."""
        self.assertFalse(run(TEMP_REPO.name, delete_build='abc123'))

    def test_run_delete_build_all(self):
        """Verify all builds can be deleted."""
        self.assertTrue(run(TEMP_REPO.name, delete_build='all'))
        self.assertEqual(0, len(list(TEMP_REPO.builds)))


if __name__ == '__main__':
    unittest.main()
