import unittest

from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
ptc.setupPloneSite()

import c2.app.zipdownload
PACKAGE_NAME = "c2.app.zipdownload"

class TestCase(ptc.PloneTestCase):
    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            zcml.load_config('configure.zcml',
                             c2.app.zipdownload)
            fiveconfigure.debug_mode = False

        @classmethod
        def tearDown(cls):
            pass


    def testQuickInstall(self):
        qi = self.portal.portal_quickinstaller
        # pprint(qi.listInstallableProducts())
        self.failUnless(PACKAGE_NAME in (p['id']
                            for p in qi.listInstallableProducts()))
        qi.installProduct(PACKAGE_NAME)
        self.failUnless(qi.isProductInstalled(PACKAGE_NAME))

def test_suite():
    return unittest.TestSuite([

        unittest.makeSuite(TestCase),

        # Unit tests
        #doctestunit.DocFileSuite(
        #    'README.txt', package='c2.app.zipdownload',
        #    setUp=testing.setUp, tearDown=testing.tearDown),

        #doctestunit.DocTestSuite(
        #    module='c2.app.zipdownload.mymodule',
        #    setUp=testing.setUp, tearDown=testing.tearDown),


        # Integration tests that use PloneTestCase
        #ztc.ZopeDocFileSuite(
        #    'README.txt', package='c2.app.zipdownload',
        #    test_class=TestCase),

        #ztc.FunctionalDocFileSuite(
        #    'browser.txt', package='c2.app.zipdownload',
        #    test_class=TestCase),

        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
