from five import grok
from collective.pdfexport.interfaces import IPDFConverter, IPDFHTMLProvider
import os
from StringIO import StringIO
import pdfkit

class PDFKitPDFConverter(grok.GlobalUtility):
    grok.implements(IPDFConverter)

    def __init__(self):
        path = os.environ.get('WKHTMLTOPDF_PATH', None)
        if path:
            config = pdfkit.configuration(wkhtmltopdf=path)
        else:
            config = pdfkit.configuration()
        self.config = config

    def convert(self, content, view=None):
        item = IPDFHTMLProvider(content)
        html = item.pdf_html(view=view)
        out = pdfkit.from_string(html, False, options={
            '--print-media-type': None,
            '--disable-javascript': None,
            '--quiet': None
            }, 
            configuration=self.config)
        return StringIO(out)


