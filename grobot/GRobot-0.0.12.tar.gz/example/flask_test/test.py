import os
from app import app
import unittest


class AppTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def tearDown(self):
        pass

    def testLogin(self):

if __name__ == '__main__':
    unittest.main()