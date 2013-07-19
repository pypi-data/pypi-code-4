from DateTime import DateTime

from zope.interface import Interface
from zope.component import adapts
from zope.i18n import MessageFactory

try:
    from plone.app.z3cform import inline_validation
except ImportError:
    # BBB Plone < 4.3 compatibility
    from plone.app.form.kss import validation as inline_validation

from Products.CMFCore.utils import getToolByName

from quintagroup.captcha.core.utils import (decrypt, parseKey, encrypt1,
                                            getWord, detectInlineValidation)

from z3c.form.validator import SimpleFieldValidator

from quintagroup.z3cform.captcha.interfaces import ICaptcha

_ = MessageFactory('quintagroup.z3cform.captcha')


class CaptchaValidator(SimpleFieldValidator):
    """Captcha validator"""

    adapts(Interface, Interface, Interface, ICaptcha, Interface)

    def validate(self, value):
        # Verify the user input against the captcha

        # Captcha validation is one-time process to prevent hacking
        # This is the reason for in-line validation to be disabled.
        if detectInlineValidation(inline_validation):
            return

        context = self.context
        request = self.request
        value = value or ''
        captcha_type = context.getCaptchaType()
        if captcha_type in ['static', 'dynamic']:
            hashkey = request.get('%shashkey' % self.widget.form.prefix, '')
            decrypted_key = decrypt(context.captcha_key, hashkey)
            parsed_key = parseKey(decrypted_key)

            index = parsed_key['key']
            date = parsed_key['date']

            if captcha_type == 'static':
                img = getattr(context, '%s.jpg' % index)
                solution = img.title
                enc = encrypt1(value)
            else:
                enc = value
                solution = getWord(int(index))

            captcha_tool = getToolByName(context, 'portal_captchas')
            captcha_tool_has_key = captcha_tool.has_key
            if (enc != solution) or (captcha_tool_has_key(decrypted_key)) or \
               (DateTime().timeTime() - float(date) > 3600):
                raise ValueError(_(u'Please re-enter validation code.'))
            else:
                captcha_tool.addExpiredKey(decrypted_key)
