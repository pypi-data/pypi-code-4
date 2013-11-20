import unittest
import doctest

from Testing import ZopeTestCase
from zope.testing import doctestunit
from zope.component import testing, eventtesting

from Testing import ZopeTestCase as ztc
from Products.PloneTestCase import ptc

from raptus.multilanguageplone.tests import base


def test_suite():
    suite = unittest.TestSuite()

    suite.addTest(
        ztc.FunctionalDocFileSuite(
            'README.txt', 
            package='raptus.multilanguageplone',
            test_class=base.FunctionalTestCase,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE |
                doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
        )
    )

    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
