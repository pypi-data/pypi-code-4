# -*- coding: utf-8 -*-
from collective.pdfpeek.conversion import AbstractPDFExtractor
from collective.pdfpeek.interfaces import IPDFDataExtractor
from plone.rfc822.interfaces import IPrimaryFieldInfo
from zope.interface import implementer


@implementer(IPDFDataExtractor)
class DexterityPDFExtractor(AbstractPDFExtractor):
    """Extract information from PDF stored in plone.app.contenttypes
       files.
    """

    @property
    def content_type(self):
        try:
            return IPrimaryFieldInfo(self.context).value.contentType
        except (TypeError, AssertionError):
            pass

    @property
    def data(self):
        try:
            return IPrimaryFieldInfo(self.context).value.data
        except (TypeError, AssertionError):
            pass
