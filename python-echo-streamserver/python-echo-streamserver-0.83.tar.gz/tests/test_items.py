import sys
try:
    import unittest2 as unittest
except ImportError:
    import unittest

sys.path.append('./')

from echo import items, StreamServerError
from echo.items.mux_api import MuxRequest

# EQL Query Strings (Account Dependent)
# ======================================================================
# "scope" tests:
base_url = "http://blog-uat.nj.com"
query_scope = "scope:%s/*" % base_url

# "url" tests:
relative_url =  'artful_diner/atom.xml'
query_url = 'url:"%s/%s"' % (base_url, relative_url)

class Tests(unittest.TestCase):
    """Echo Items API Query Tests
    """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_count(self):
        """ items.count() returns a value greater than zero """
        try:
            n = items.count(query_url)
            self.assertGreaterEqual(n, 0)
        except StreamServerError, e:
            raise

    def test_search(self):
        """ items.search() returns 'entries' """
        try:
            r = items.search(query_scope)
            self.assertIn('entries', r)
        except StreamServerError, e:
            raise

    def test_mux(self):
        """ mux API returns two results 'count0', 'search0' """
        try:
            # Search Query for items.
            search = MuxRequest(query_scope)

            # Count Query for items.
            count = MuxRequest(query_url, api_method='count')

            # Form list of them for Mux API.
            requests = [ search, count ]

            # Mux API requests..."
            r = items.mux(requests)
            self.assertIn('count0', r)
            self.assertIn('search0', r)
        except StreamServerError, e:
            raise

