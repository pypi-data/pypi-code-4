#####################################################################
# zopyx.authoring
# (C) 2011, ZOPYX Limited, D-72070 Tuebingen. All rights reserved
#####################################################################

import os
import cssutils
import unittest2
from ..contentfolder import cleanup_css

package_home = os.path.dirname(__file__)

CSS1_IN = os.path.join(package_home, '1.css')
CSS1_EXPECTED = os.path.join(package_home, '1.css_expected')

def _parse_css(css):
    sheet = cssutils.parseString(css)
    cssutils.ser.prefs.indent = '  '
    return sheet.cssText


class OfficeImport(unittest2.TestCase):

    def testCleanupCSS(self):

        css = file(CSS1_IN).read()
        css_after_cleanup = cleanup_css(css)
        css_expected = _parse_css(file(CSS1_EXPECTED).read())
        self.assertEqual(css_expected, css_after_cleanup)
        

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(OfficeImport))
    return suite

