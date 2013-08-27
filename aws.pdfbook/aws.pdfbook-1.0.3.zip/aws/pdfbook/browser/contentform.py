# -*- coding: utf-8 -*-
# $Id: contentform.py 247098 2011-12-07 14:31:17Z vincentfretin $
"""Form for PDF print and options"""
import os
from zope.component import getMultiAdapter
from zope.formlib import form
from Acquisition import aq_inner
try: # Plone 4.1+
    from five.formlib.formbase import PageForm
except ImportError:
    from Products.Five.formlib.formbase import PageForm

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.ATContentTypes import ATCTMessageFactory as atct_
from aws.pdfbook.interfaces import IPrintOptions
from aws.pdfbook.conversions import makePDF
from aws.pdfbook import translate as _
from aws.pdfbook.config import DOWNLOAD_BUFFER_SIZE


class PDFBookPrint(PageForm):
    """Form with options that generates the pdf"
    """

    template = ViewPageTemplateFile('templates/pdfbookprint.pt')
    form_fields = form.FormFields(IPrintOptions)

    @form.action(atct_(u'label_download_as_pdf', default=u"Download PDF"))
    def handlePDF(self, action, options):
        """making and downloading PDF
        """
        html = self._makeHTML(options)
        context = aq_inner(self.context)
        info = makePDF(html, context, self.request)

        pdf_filepath = info.pdf_filepath
        pdf_filename = os.path.basename(pdf_filepath)
        response = self.request.RESPONSE
        setHeader = response.setHeader
        setHeader('Content-type', 'application/pdf')
        setHeader('Content-length', str(os.stat(pdf_filepath)[6]))
        mode = {True: 'inline', False:'attachment'}[options['inline_render']]
        setHeader('Content-disposition',
                  '%s; filename=%s' % (mode, pdf_filename))

        fp = open(pdf_filepath, 'rb')
        while True:
            data = fp.read(DOWNLOAD_BUFFER_SIZE)
            if data:
                response.write(data)
            else:
                break
        fp.close()
        return


    @form.action(_(u'label_view_as_printable', default=u"View a printable page"))
    def handleHTML(self, action, options):
        """HTML preview
        """
        return self._makeHTML(options)


    def _makeHTML(self, options):
        """Making HTML with potential options
        """
        html_engine = getMultiAdapter((self.context, self.request), name=u'printlayout')
        return html_engine(context=self.context, request=self.request, options=options)

