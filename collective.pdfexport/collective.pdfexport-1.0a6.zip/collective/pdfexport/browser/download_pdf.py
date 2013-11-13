from five import grok
from collective.pdfexport.interfaces import IPDFExportCapable
import xhtml2pdf.pisa as pisa
from StringIO import StringIO
from collective.pdfexport.interfaces import IPDFConverter
from zope.component import getUtility
from Products.CMFCore.interfaces import IContentish

class PDFExportView(grok.View):
    grok.name('download_pdf')
    grok.context(IContentish)

    def render(self):
        converter = getUtility(IPDFConverter)
        view = self.request.get('pdf-view', None)
        result = converter.convert(self.context, view=view)
        out = result.getvalue()
        self.request.response.setHeader('Content-Type', 'application/pdf')
        if not self.request.get('pdf-noattach', False):
            self.request.response.setHeader('Content-Disposition', 
                'attachment; filename=%s.pdf' % self.context.getId())
        self.request.response.setHeader('Content-Length', len(out))
        return out

