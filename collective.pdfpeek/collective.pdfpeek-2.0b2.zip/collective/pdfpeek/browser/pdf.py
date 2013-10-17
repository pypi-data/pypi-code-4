# -*- coding: utf-8 -*-
from Acquisition import aq_inner

from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from Products.Five.browser import BrowserView
from plone.registry.interfaces import IRegistry
from collective.pdfpeek.interfaces import IPDFPeekConfiguration
from collective.pdfpeek.interfaces import IPDF


class PdfImageAnnotationView(BrowserView):
    """view class used to access the image thumbnails that pdfpeek
       annotates on ATFile objects.
    """
    @property
    def num_pages(self):
        context = aq_inner(self.context)
        annotations = IAnnotations(context)
        if annotations['pdfpeek']['image_thumbnails']:
            annotations_len = len(annotations['pdfpeek']['image_thumbnails'])
            num_pages = range(annotations_len / 2)
        else:
            num_pages = 0
        return num_pages


class IsPdfView(BrowserView):
    """check to see if the object is a PDF
    """
    @property
    def is_pdf(self):
        if IPDF.providedBy(self.context):
            return True
        return False


class IsPreviewOnView(BrowserView):
    """
    check to see if the image previews are on.
    """
    @property
    def previews_on(self):
        registry = getUtility(IRegistry)
        config = registry.forInterface(IPDFPeekConfiguration)
        if config.preview_toggle is True:
            return True
        return False
