#!/usr/bin/env python

"""
Unit tests for the veracity.builder module.
"""

import unittest

import os

from veracity.builder import Builder, run
from veracity.objects import Repository
from veracity.common import Config

from veracity.test import TEST_REPO, TEMP_REPO_NAME, REASON, FILES, log


class TestBuilder(unittest.TestCase):  # pylint: disable=R0904
    """Tests for the Builder class."""  # pylint: disable=C0103

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
class TestRun(unittest.TestCase):
    """Tests for the main builder interface."""  # pylint: disable=C0103

    @classmethod
    def setUpClass(cls):
        if TEST_REPO:
            cls.repo = Repository(TEMP_REPO_NAME, remote=TEST_REPO, autosync=False)

    @classmethod
    def tearDownClass(cls):
        if TEST_REPO:
            cls.repo.delete()

    def test_run_valid(self):
        """Verify a builder can be run."""
        del self.repo.builds
        self.repo.request_build('test', 'C', 'M', 'Q', self.repo.heads[0], branch='master')
        self.assertTrue(run(Config(path=os.path.join(FILES, 'builder.cfg'), repos=[self.repo.name], envs=['M'])))
        self.assertIsNone(self.repo.get_build('M', 'Q'))
        self.assertTrue(run(Config(path=os.path.join(FILES, 'builder.cfg'), repos=[self.repo.name], envs=['M'])))

    def test_run_valid_test(self):
        """Verify a builder can be run in test mode."""
        self.assertTrue(run(Config(path=os.path.join(FILES, 'builder.cfg'), repos=[self.repo.name]), test=True))

    def test_run_valid_test_step(self):
        """Verify a builder step can be run in test mode."""
        self.assertTrue(run(Config(path=os.path.join(FILES, 'builder.cfg'), repos=[self.repo.name]), test='U'))

    def test_run_invalid(self):
        """Verify a poller returns an error with no repository."""
        self.assertFalse(run(Config()))


if __name__ == '__main__':
    unittest.main()
