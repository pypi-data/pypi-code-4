# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets import ViewletBase


class PdfpeekViewlet(ViewletBase):
    """This viewlet displays the pdfpeek interface
    """

    index = ViewPageTemplateFile('templates/pdfpeek.pt')

