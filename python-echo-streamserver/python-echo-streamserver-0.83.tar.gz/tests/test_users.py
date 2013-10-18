import sys
try:
    import unittest2 as unittest
except ImportError:
    import unittest

sys.path.append('./')

from echo import users, StreamServerError

# User Info Dictionary Sample
# ======================================================================
IDENTITY_URL='http://example.com/users/john'
USER_INFO={ 'echo': {'state': 'Untouched'},
  'poco': { 'entry': { 'accounts': [ { 'emails': [ { 'primary': 'true',
                                                     'value': 'johnQpublic@example.com'}],
                                       'identityUrl': 'http://example.com/users/john',
                                       'username': 'John'},
                                     { 'identityUrl': 'http://john.foobar.com/'}],
                       'id': 'f4062c6a6cef2a871161c5974f1daf0d'},
            'itemsPerPage': 1,
            'startIndex': 0,
            'totalResults': 1}}

class Tests(unittest.TestCase):
    """Echo Users API Tests
    """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_user(self):
        """ users.get() returns the valid info for identity URL """
        try:
            u = users.get(IDENTITY_URL)
            self.assertEqual(u, USER_INFO)
        except StreamServerError, e:
            raise

