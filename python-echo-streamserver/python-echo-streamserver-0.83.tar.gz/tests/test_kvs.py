import sys
try:
    import unittest2 as unittest
except ImportError:
    import unittest

sys.path.append('./')

from echo import kvs, StreamServerError

# Key-Value Data is translated to it repr(v) and sent to KVS.
# ======================================================================
TEST_KEY='test_key'
TEST_VALUE={
            'greeting': u'hello world',
            'shopping': [ 'soda', 'apples', 'lettuce' ],
}

class Tests(unittest.TestCase):
    """Echo Key-Value Store API Tests
    """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_delete(self):
        """ kvs.delete() succeeds """
        try:
            r = kvs.put(TEST_KEY, TEST_VALUE)
            self.assertTrue(r)
            r2 = kvs.delete(TEST_KEY)
            self.assertTrue(r2)
        except StreamServerError, e:
            raise

    def test_get(self):
        """ kvs.get() returns the same object as kvs.put() """
        try:
            r = kvs.put(TEST_KEY, TEST_VALUE)
            self.assertTrue(r)
            v = kvs.get(TEST_KEY)
            self.assertEqual(v, TEST_VALUE)
            kvs.delete(TEST_KEY)
        except StreamServerError, e:
            raise

    def test_put(self):
        """ kvs.put() succeeds """
        try:
            r = kvs.put(TEST_KEY, TEST_VALUE)
            self.assertTrue(r)
            kvs.delete(TEST_KEY)
        except StreamServerError, e:
            raise

    def _delete_not_found(self):
        kvs.delete(TEST_KEY + '_garbage', raise_not_found=True)

    def test_delete_not_found(self):
        """ kvs.delete('missing key') raises StreamServerError when raise_not_found=True """
        self.assertRaises(StreamServerError, self._delete_not_found)

    def _get_not_found(self):
        kvs.get(TEST_KEY + '_garbage', raise_not_found=True)

    def test_get_not_found(self):
        """ kvs.get('missing key') raises StreamServerError when raise_not_found=True """
        self.assertRaises(StreamServerError, self._get_not_found)

