
from unittest import TestCase

from rattail import core


class TestCore(TestCase):

    def test_get_uuid(self):
        uuid = core.get_uuid()
        self.assertIsInstance(uuid, str)
        self.assertEqual(len(uuid), 32)
