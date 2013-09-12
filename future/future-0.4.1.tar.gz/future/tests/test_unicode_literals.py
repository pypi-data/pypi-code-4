'''
Tests to ensure that the u'' prefixes on unicode strings are not removed.
Removing the prefixes on Py3.3+ is unnecessary and loses some information
-- namely, that the strings have explicitly been marked as unicode,
rather than just our guess (perhaps incorrect) that they should be
unicode.
'''
from __future__ import absolute_import, print_function
from future.builtins.backports import super

import unittest


class TestUnicodeLiterals(unittest.TestCase):
    def test_fix_unicode_literals(self):
        pass


if __name__ == '__main__':
    unittest.main()
