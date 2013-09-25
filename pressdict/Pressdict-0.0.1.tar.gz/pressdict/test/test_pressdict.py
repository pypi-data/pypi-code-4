import unittest

from pressdict import Pressdict


class PressdictTests(unittest.TestCase):

    def test_basic_functionality(self):
        pd = Pressdict()
        pd["test"] = {"key": "value", "key2": 2}
        self.assertEqual(pd["test"], {"key": "value", "key2": 2})
