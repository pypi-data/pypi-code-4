#!/usr/bin/env python

"""
Unit tests for the veracity.tracking module.
"""

import unittest

# from veracity.poller import Poller
from veracity.common import Config
from veracity.tracking import run

from veracity.test import TEST_REPO, REASON


@unittest.skipUnless(TEST_REPO, REASON)  # pylint: disable=R0904
class TestRun(unittest.TestCase):  # pylint: disable=R0904
    """Tests for the main tracking interface."""  # pylint: disable=C0103

    def test_run_tbd(self):  # TODO: replace with a real test
        self.assertTrue(run(Config(repos=[TEST_REPO.name])))


if __name__ == '__main__':
    unittest.main()
