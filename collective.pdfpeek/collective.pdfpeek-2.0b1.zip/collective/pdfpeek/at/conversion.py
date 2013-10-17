# -*- coding: utf-8 -*-
from collective.pdfpeek.conversion import AbstractPDFExtractor
from collective.pdfpeek.interfaces import IPDFDataExtractor
from zope.interface import implementer


@implementer(IPDFDataExtractor)
class ArchetypePDFExtractor(AbstractPDFExtractor):
    """Extract information from PDF stored in ATFiles.
    """

    @property
    def content_type(self):
        return self.context.getFile().getContentType()

    @property
    def data(self):
        return self.context.getFile().get_data()
