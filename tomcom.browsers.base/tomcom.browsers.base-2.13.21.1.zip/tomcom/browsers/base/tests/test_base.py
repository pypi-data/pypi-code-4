import unittest
from tomcom.browsers.base import BrowserView

class TestBase(unittest.TestCase):

    def test_sample(self):
        BrowserView(object(),object())

if __name__ == '__main__':
    unittest.main()
