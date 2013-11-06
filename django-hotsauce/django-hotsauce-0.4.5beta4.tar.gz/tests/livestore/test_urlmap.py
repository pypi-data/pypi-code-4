from notmm.utils.urlmap import RegexURLMap
from test_support import unittest

class SatchmoURLMapTestCase(unittest.TestCase):

    def setUp(self):
        self.urlmap = RegexURLMap(label='satchmo-0.9 test')
    
    def test_include(self):
        self.urlmap.include('livestore.test_urls')
        

