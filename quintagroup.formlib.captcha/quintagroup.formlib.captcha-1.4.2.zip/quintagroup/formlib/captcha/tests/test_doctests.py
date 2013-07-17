import unittest
import doctest

from Products.Five import zcml
from Products.Five import fiveconfigure

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
from Testing import ZopeTestCase as ztc

from quintagroup.captcha.core.utils import decrypt, parseKey, getWord
from quintagroup.captcha.core.tests.base import testPatch
from quintagroup.captcha.core.tests.testWidget import addTestLayer


class FormlibCaptchaLayer(PloneSite):
    @classmethod
    def setUp(cls):
        fiveconfigure.debug_mode = True
        import quintagroup.captcha.core
        import quintagroup.formlib.captcha
        zcml.load_config('configure.zcml', quintagroup.formlib.captcha)
        zcml.load_config('tests.zcml', quintagroup.formlib.captcha.tests)
        fiveconfigure.debug_mode = False
        ztc.installPackage('quintagroup.captcha.core')

    @classmethod
    def tearDown(cls):
        pass

ptc.setupPloneSite(extension_profiles=['quintagroup.captcha.core:default', ])


class FormlibCaptchaTestCase(ptc.FunctionalTestCase):
    layer = FormlibCaptchaLayer

    def afterSetUp(self):
        # prepare context
        self.loginAsPortalOwner()
        testPatch()
        addTestLayer(self)
        # prepare captcha data
        captcha_key = self.portal.captcha_key
        self.hashkey = self.portal.getCaptcha()
        decrypted = decrypt(captcha_key, self.hashkey)
        self.captcha_word = getWord(int(parseKey(decrypted)['key']) - 1)


def test_suite():
    return unittest.TestSuite([

        # Demonstrate the main content types
        ztc.ZopeDocFileSuite(
            'README.txt', package='quintagroup.formlib.captcha',
            test_class=FormlibCaptchaTestCase,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE |
            doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),
    ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
