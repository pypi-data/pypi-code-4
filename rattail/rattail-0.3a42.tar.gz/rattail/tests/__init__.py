
import unittest

from pyramid import testing


class TestCase(unittest.TestCase):
    """
    Base class for all test suites.
    """

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_something(self):
        self.assertTrue(1)
