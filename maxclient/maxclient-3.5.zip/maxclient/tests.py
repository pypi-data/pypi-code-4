import unittest
from maxclient import MaxClient


class ClientUnitTests(unittest.TestCase):
    def test_login(self):
        client = MaxClient()
        token = client.login()
        self.assertEqual(len(token), 32)
