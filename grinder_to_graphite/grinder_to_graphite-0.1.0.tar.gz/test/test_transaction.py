import unittest
from g2g.logtype.grinder.transaction import HTTPTest, NonHTTPTest

"""
Thread, Run, Test, Start time (ms since Epoch), Test time, Errors, HTTP response code,
HTTP response length, HTTP response errors, Time to resolve host, Time to establish connection,
Time to first byte, New connections
0, 0, 2, 1377884275587, 368, 0, 200, 132, 0, 0, 166, 359, 1
"""


class TestHTTPTransaction(unittest.TestCase):
    def testCreateHTTPTx(self):
        words = "0, 0, 2, 1377884275587, 368, 0, 200, 132, 0, 0, 166, 359, 1".split(", ")
        tx = HTTPTest(words)
        self.assertEqual(tx.time, 368.0)
        self.assertEqual(tx.establish_connect_time, 166.0)
        self.assertEqual(tx.new_connections, 1)


class TestNonHTTPTransaction(unittest.TestCase):
    def testCreateNonHTTPPx(self):
        words = "0, 0, 2, 1377884275587, 368, 0".split(", ")
        tx = NonHTTPTest(words)
        self.assertEqual(tx.errors, 0.0)
        self.assertEqual(tx.time, 368.0)
