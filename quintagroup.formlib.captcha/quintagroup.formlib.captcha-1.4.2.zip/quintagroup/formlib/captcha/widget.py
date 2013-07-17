from DateTime import DateTime

try:
    from zope.site.hooks import getSite
    getSite()
except ImportError:
    from zope.app.component.hooks import getSite
from zope.app.form.browser import ASCIIWidget
from zope.app.form.interfaces import ConversionError
from zope.app.form.browser.widget import renderElement
from zope.i18n import MessageFactory

from Acquisition import aq_parent

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import ISiteRoot

from quintagroup.captcha.core.utils import (decrypt, parseKey,
                                            encrypt1, getWord,
                                            detectInlineValidation)

try:
    from plone.app.form import inline_validation
except ImportError:
    # BBB Plone < 4.3 compatibility.
    # The implementation of inline validation was switched
    # to a non-KSS-based in plone.app.form-2.2.0
    try:
        from plone.app.form.kss import validation as inline_validation
    # BBB: Plone 3.0 compatibility.
    # The KSS validation was added in plone.app.form-1.1.0.
    except:
        inline_validation = None

_ = MessageFactory('quintagroup.formlib.captcha')

import logging

logger = logging.getLogger('quintagroup.formlib.captcha')


class CaptchaWidget(ASCIIWidget):

    def get_site(self):
        # get from plone.app.form.widgets.wysiwygwdget
        site = getSite()
        while site is not None and not ISiteRoot.providedBy(site):
            site = aq_parent(site)
        return site

    def __call__(self):
        kwargs = {'type': self.type,
                  'name': self.name,
                  'id': self.name,
                  'cssClass': self.cssClass,
                  'style': self.style,
                  'size': self.displayWidth,
                  'extra': self.extra}

        site = self.get_site()
        portal_url = getToolByName(site, 'portal_url')()
        key = site.getCaptcha()

        if self._prefix:
            prefix = '%s.' % self._prefix
        else:
            prefix = ''

        return u"""<input type="hidden" value="%s" name="%shashkey" />
                   %s
                   <img src="%s/getCaptchaImage/%s"
                        alt="Enter the word"/>""" % (key,
                                                     prefix,
                                                     renderElement(self.tag,
                                                                   **kwargs),
                                                     portal_url,
                                                     key)

    def hasInput(self):
        # The validator looks for the captcha only if the captcha field
        # is present. If the captcha field is omitted from the request,
        # then the captcha validation never happens. That's why 'required'
        # option is useless. So, we have to simulate 'required': set up 'True'
        # for the captcha input.
        return True

    def _getFormInput(self):
        """ It returns current form input. """
        # The original method isn't suitable when the captcha field
        # is omitted from the request.
        return self.request.get(self.name, u'')

    def _toFieldValue(self, input):
        # Captcha validation is one-time process to prevent hacking
        # This is the reason for in-line validation to be disabled.
        if inline_validation and detectInlineValidation(inline_validation):
            return input

        # Verify the user input against the captcha.
        # Get captcha type (static or dynamic)
        site = self.get_site()
        captcha_type = site.getCaptchaType()

        # validate captcha input
        if input and captcha_type in ['static', 'dynamic']:
            # make up form prefix
            if self._prefix:
                prefix = '%s.' % self._prefix
            else:
                prefix = ''

            hashkey = self.request.get('%shashkey' % prefix, '')
            decrypted_key = decrypt(site.captcha_key, hashkey)
            parsed_key = parseKey(decrypted_key)

            index = parsed_key['key']
            date = parsed_key['date']

            if captcha_type == 'static':
                img = getattr(site, '%s.jpg' % index)
                solution = img.title
                enc = encrypt1(input)
            else:
                enc = input
                solution = getWord(int(index))

            captcha_tool = getToolByName(site, 'portal_captchas')
            if (enc != solution) or (decrypted_key in captcha_tool.keys()) or \
               (DateTime().timeTime() - float(date) > 3600):
                raise ConversionError(_(u'Please re-enter validation code.'))
            else:
                captcha_tool.addExpiredKey(decrypted_key)

        return super(CaptchaWidget, self)._toFieldValue(input)
