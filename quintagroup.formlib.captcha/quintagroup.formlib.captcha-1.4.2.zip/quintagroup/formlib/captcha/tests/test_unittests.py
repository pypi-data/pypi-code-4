import re
import unittest

from zope.schema.interfaces import IField
from zope.component import queryMultiAdapter
from zope.publisher.browser import TestRequest
from zope.app.form.interfaces import IInputWidget
from zope.app.form.interfaces import ConversionError

from Products.Five import zcml
from Products.Five import fiveconfigure
from Testing import ZopeTestCase as ztc
from Products.PloneTestCase.layer import onsetup
from Products.PloneTestCase import PloneTestCase as ptc

from quintagroup.captcha.core.utils import decrypt, parseKey, getWord
from quintagroup.captcha.core.tests.base import testPatch
from quintagroup.captcha.core.tests.testWidget import addTestLayer

from quintagroup.formlib.captcha import Captcha
from quintagroup.formlib.captcha import CaptchaWidget


@onsetup
def setup_product():
    fiveconfigure.debug_mode = True
    import quintagroup.captcha.core
    import quintagroup.formlib.captcha
    zcml.load_config('configure.zcml', quintagroup.formlib.captcha)
    fiveconfigure.debug_mode = False
    ztc.installPackage('quintagroup.captcha.core')

setup_product()
ptc.setupPloneSite(extension_profiles=['quintagroup.captcha.core:default', ])


class TestRegistrations(ptc.PloneTestCase):

    def testCaptchaFieldInterface(self):
        self.assertEqual(IField.implementedBy(Captcha), True)

    def testCaptchaWidgetInterface(self):
        self.assertEqual(IInputWidget.implementedBy(CaptchaWidget), True)

    def testWidgetRegistration(self):
        cfield = Captcha()
        request = TestRequest()
        cwidget = queryMultiAdapter((cfield, request), IInputWidget)
        self.assertNotEqual(cwidget, None)


class TestCaptchaWidgetHTML(ptc.PloneTestCase):
    def afterSetUp(self):
        # app context
        self.loginAsPortalOwner()
        # get html output from widget
        field = Captcha()
        bound = field.bind(self.portal)
        widget = CaptchaWidget(bound, self.app.REQUEST)
        widget.setPrefix('')
        self.html = widget()

    def testHidden(self):
        HIDDENTAG = '<input\s+[^>]*(?:' \
            '(?:type="hidden"\s*)|' \
            '(?:name="hashkey"\s*)|' \
            '(?:value="(?P<value>[0-9a-fA-F]+)"\s*)' \
            '){3}/>'
        hidden = re.search(HIDDENTAG, self.html)
        self.assertTrue(hidden and hidden.group('value'))

    def testImg(self):
        IMAGETAG = '<img\s+[^>]*src=\"' \
            '(?P<src>[^\"]*/getCaptchaImage/[0-9a-fA-F]+)' \
            '\"[^>]*>'
        img = re.search(IMAGETAG, self.html)
        self.assertTrue(img and img.group('src'))

    def testTextField(self):
        FIELDTAG = '<input\s+[^>]*type=\"text\"\s*[^>]*>'
        self.assertEqual(re.search(FIELDTAG, self.html) is not None, True)


class TestCaptchaWidgetToField(ptc.PloneTestCase):

    def afterSetUp(self):
        # prepare context
        self.loginAsPortalOwner()
        testPatch()
        addTestLayer(self)
        self.captcha_key = self.portal.captcha_key
        # prepare widget
        field = Captcha()
        bound = field.bind(self.portal)
        self.request = self.app.REQUEST
        self.widget = CaptchaWidget(bound, self.request)
        self.widget.setPrefix('')
        # prepare captcha data
        self.hashkey = self.portal.getCaptcha()
        self.request.form['hashkey'] = self.hashkey

    def testSubmitRightCaptcha(self):
        decrypted = decrypt(self.captcha_key, self.hashkey)
        key = getWord(int(parseKey(decrypted)['key']) - 1)
        try:
            res = self.widget._toFieldValue(key)
        except ConversionError, e:
            self.fail("Rised unexpected %s error on right captcha submit" %
                      e.doc())
        else:
            self.assertEqual(res, key)

    def testSubmitWrongCaptcha(self):
        try:
            self.widget._toFieldValue("wrong key")
        except ConversionError, e:
            self.assertEqual(e.doc(), u'Please re-enter validation code.')
        else:
            self.fail("No ConversionError rised on wrong captcha key submit")

    def testSubmitRightCaptchaTwice(self):
        decrypted = decrypt(self.captcha_key, self.hashkey)
        key = getWord(int(parseKey(decrypted)['key']) - 1)
        self.widget._toFieldValue(key)
        try:
            self.widget._toFieldValue(key)
        except ConversionError, e:
            self.assertEqual(e.doc(), u'Please re-enter validation code.')
        else:
            self.fail("No ConversionError rised on right captcha key "
                      "submitting twice")


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestRegistrations))
    suite.addTest(unittest.makeSuite(TestCaptchaWidgetHTML))
    suite.addTest(unittest.makeSuite(TestCaptchaWidgetToField))
    return suite
