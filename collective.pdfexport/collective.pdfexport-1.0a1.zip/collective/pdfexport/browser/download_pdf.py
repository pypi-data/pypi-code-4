from five import grok
from collective.pdfexport.interfaces import IPDFExportCapable
import xhtml2pdf.pisa as pisa
from StringIO import StringIO

class PDFExportView(grok.View):
    grok.name('download_pdf')
    grok.context(IPDFExportCapable)

    def render(self):
        html = self.context.restrictedTraverse('xhtml2pdf_view')().encode('utf-8')
        result = StringIO()
        pdf = pisa.CreatePDF(StringIO(html), result)
        out = result.getvalue()
        self.request.response.setHeader('Content-Type', 'application/pdf')
        self.request.response.setHeader('Content-Disposition', 
            'attachment; filename=%s.pdf' % self.context.getId())
        self.request.response.setHeader('Content-Length', len(out))
        return out

