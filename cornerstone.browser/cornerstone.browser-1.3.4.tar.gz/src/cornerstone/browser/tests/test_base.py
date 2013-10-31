#
# Copyright 2008, BlueDynamics Alliance, Austria - http://bluedynamics.com
#
# GNU General Public Licence Version 2 or later - see LICENCE.GPL

__author__ = """Robert Niederreiter <rnix@squarewave.at>"""
__docformat__ = 'plaintext'

from pprint import pprint
import interlude
import unittest
from zope.testing import doctest
from zope.app.testing.placelesssetup import setUp, tearDown
from zope.configuration.xmlconfig import XMLConfig

optionflags = doctest.NORMALIZE_WHITESPACE | \
              doctest.ELLIPSIS # | \
              #doctest.REPORT_ONLY_FIRST_FAILURE

TESTFILES = [
    'base.txt',
    'tmpl.txt'
]

def test_suite():
    setUp()
    import zope.app.component
    XMLConfig('meta.zcml', zope.app.component)()
    #import Products.Five
    #XMLConfig('meta.zcml', Products.Five)()
    import cornerstone.browser
    XMLConfig('base.zcml', cornerstone.browser)()
    
    return unittest.TestSuite([
        doctest.DocFileSuite(
            file, 
            package="cornerstone.browser",
            optionflags=optionflags,
            globs=dict(interact=interlude.interact, pprint=pprint),
        ) for file in TESTFILES
    ])
    tearDown()

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite') 

