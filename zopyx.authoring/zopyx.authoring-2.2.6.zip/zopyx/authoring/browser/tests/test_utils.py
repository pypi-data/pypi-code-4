#####################################################################
# zopyx.authoring
# (C) 2011, ZOPYX Limited, D-72070 Tuebingen. All rights reserved
#####################################################################

import unittest2
from .. import util

TABLE_HTML = '<table id="foo"><tr><td>hello world</td></tr></table>'

class TestUtils(unittest2.TestCase):

    def testExtractTableExisting(self):
        table_html = util.extract_table(TABLE_HTML, 'foo')
        self.assertEqual(table_html.startswith('<table id="foo">'), True)
        
    def testExtractTableNonExisting(self):
        table_html = util.extract_table(TABLE_HTML, 'var')
        self.assertEqual(table_html, '')

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestUtils))
    return suite

