import logging
log = logging.getLogger('seantis.plonetools')

from urlparse import urlparse
from zope.schema import TextLine, URI
from zope.schema.interfaces import InvalidURI

from zope.interface import Invalid

from Products.CMFDefault.utils import checkEmailAddress
from Products.CMFDefault.exceptions import EmailAddressInvalid

from seantis.plonetools import _


class Email(TextLine):

    def __init__(self, *args, **kwargs):
        super(TextLine, self).__init__(*args, **kwargs)

    def _validate(self, value):
        super(TextLine, self)._validate(value)
        validate_email(value)


class Website(URI):
    """URI field which assumes http:// if no protocol is specified."""

    def fromUnicode(self, value):
        try:
            if not urlparse(value).scheme:
                value = u'http://' + value
        except:
            log.exception('invalid url %s' % value)
            raise InvalidURI(value)

        return super(Website, self).fromUnicode(value)


def validate_email(value):
    try:
        if value:
            checkEmailAddress(value)
    except EmailAddressInvalid:
        raise Invalid(_(u'Invalid email address'))
    return True


try:
    from plone.schemaeditor.fields import FieldFactory
    EmailFactory = FieldFactory(Email, _(u'Email'))
    WebsiteFactory = FieldFactory(
        Website, _(u'Website')
    )
except ImportError:
    pass


try:
    from plone.supermodel.exportimport import BaseHandler
    EmailHandler = BaseHandler(Email)
    WebsiteHandler = BaseHandler(Website)
except ImportError:
    pass
