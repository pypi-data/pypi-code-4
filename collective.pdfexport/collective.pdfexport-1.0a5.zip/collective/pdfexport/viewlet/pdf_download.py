from Acquisition import aq_inner
from zope.interface import Interface
from five import grok
from zope.component import getMultiAdapter
from Products.CMFCore.interfaces import IContentish
from plone.app.layout.viewlets import interfaces as manager
from collective.pdfexport.interfaces import IProductSpecific
import os
import copy
import urllib

grok.templatedir('templates')

class PDFDownload(grok.Viewlet):
    grok.context(IContentish)
    grok.viewletmanager(manager.IBelowContentTitle)
    grok.template('pdf_download')
    grok.layer(IProductSpecific)

    def available(self):
        return True

    def pdf_url(self):
        view_name = os.path.basename(self.request.getURL())
        params = copy.copy(self.request.form)

        if view_name != 'view':
            params['pdf-view'] = view_name

        if not params:
            return '%s/download_pdf' % self.context.absolute_url()

        qs = urllib.urlencode(params)
        return '%s/download_pdf?%s' % (self.context.absolute_url(), qs)
