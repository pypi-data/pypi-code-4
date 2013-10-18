import sys
try:
    import unittest2 as unittest
except ImportError:
    import unittest

sys.path.append('./')

from echo import eql, StreamServerError

# EQL Query Strings (Account Dependent)
# ======================================================================
# "scope" tests:
base_url = "http://blog-uat.mlive.com"
query1 = 'scope:"%s/*"' % base_url

class Tests(unittest.TestCase):
    """Echo EQL Query Composition API Tests
    """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_query(self):
        """ Create default 'scope:' Query """
        try:
            q = eql.Query(base_url)
            self.assertEqual(str(q), query1)
        except StreamServerError, e:
            raise

