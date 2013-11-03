from Acquisition import aq_inner
from zope.interface import Interface
from five import grok
from zope.component import getMultiAdapter
from Products.CMFCore.interfaces import IContentish
from plone.app.layout.viewlets import interfaces as manager
from collective.pdfexport.interfaces import IProductSpecific
import os

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
        if view_name == 'view':
            return '%s/download_pdf' % self.context.absolute_url()
        return '%s/download_pdf?view=%s' % (self.context.absolute_url(),
                                            view_name)
