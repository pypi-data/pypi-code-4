#!/usr/bin/env python

"""
Unit tests for the veracity.builder module.
"""

import unittest

import os

from veracity.builder import Builder, run
from veracity.common import Config

from veracity.test import TEST_REPO, REASON, FILES, log, create_temp_repo, delete_temp_repo


def setUpModule():  # pylint: disable=C0103
    """Create a temporary repository for this module's tests.
    """
    global TEMP_REPO  # pylint: disable=W0601
    TEMP_REPO = create_temp_repo(__name__)


def tearDownModule():  # pylint: disable=C0103
    """Delete the temporary repository.
    """
    delete_temp_repo(__name__, TEMP_REPO)


@unittest.skipUnless(TEST_REPO, REASON)  # pylint: disable=R0904
class TestBuilder(unittest.TestCase):  # pylint: disable=R0904
    """Integration tests for the Builder class."""  # pylint: disable=C0103

    def test_from_config(self):
        """Verify a poller can be created from a config."""
        builder1 = Builder(TEST_REPO.name, Config(envs=['W']))
        builder2 = Builder(TEST_REPO.name, Config(envs=['W']))
        builder3 = Builder(TEST_REPO.name, Config(envs=['L']))
        log(builder1, builder2, builder3)
        self.assertEqual(builder1, builder2)
        self.assertNotEqual(builder1, builder3)
        self.assertNotEqual(builder1, TEST_REPO.name)


@unittest.skipUnless(TEST_REPO, REASON)  # pylint: disable=R0904
class TestRun(unittest.TestCase):  # pylint: disable=R0904
    """Integration tests for the main builder interface."""  # pylint: disable=C0103

    def test_run_valid(self):
        """Verify a builder can be run."""
        del TEMP_REPO.builds
        TEMP_REPO.request_build('test', 'C', 'M', 'Q', TEMP_REPO.heads[0], branch='master')
        self.assertTrue(run(Config(path=os.path.join(FILES, 'builder.cfg'), repos=[TEMP_REPO.name], envs=['M'])))
        self.assertIsNone(TEMP_REPO.get_build('M', 'Q'))
        self.assertTrue(run(Config(path=os.path.join(FILES, 'builder.cfg'), repos=[TEMP_REPO.name], envs=['M'])))

    def test_run_valid_test(self):
        """Verify a builder can be run in test mode."""
        self.assertTrue(run(Config(path=os.path.join(FILES, 'builder.cfg'), repos=[TEMP_REPO.name]), test=True))

    def test_run_valid_test_step(self):
        """Verify a builder step can be run in test mode."""
        self.assertTrue(run(Config(path=os.path.join(FILES, 'builder.cfg'), repos=[TEMP_REPO.name]), test='U'))

    def test_run_valid_request_delete(self):
        """Verify an invalid build request gets deleted."""
        del TEMP_REPO.builds
        TEMP_REPO.request_build('test', 'C', 'W', 'Q', 1, branch='master')
        self.assertTrue(run(Config(repos=[TEMP_REPO.name], envs=['W'])))

    def test_run_invalid(self):
        """Verify a poller returns an error with no repository."""
        self.assertFalse(run(Config()))


if __name__ == '__main__':
    unittest.main()
