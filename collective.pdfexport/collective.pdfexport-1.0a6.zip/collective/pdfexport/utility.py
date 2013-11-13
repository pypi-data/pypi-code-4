from five import grok
from collective.pdfexport.interfaces import IPDFConverter, IPDFHTMLProvider
import os
from StringIO import StringIO
import pdfkit
from base64 import b64encode
from pdfkit.pdfkit import PDFKit

_orig_command = PDFKit.command

def command(self, path=None):
    args = _orig_command(self, path)
    auth = os.environ.get('WKHTMLTOPDF_HTTPAUTH', None)
    if auth:
        username, password = auth.strip().split(':', 1)
        args.insert(1, 'Basic %s' % b64encode(auth.strip()))
        args.insert(1, 'Authorization')
        args.insert(1, '--custom-header')
    return args

PDFKit.command = command

class PDFKitPDFConverter(grok.GlobalUtility):
    grok.implements(IPDFConverter)

    def __init__(self):
        path = os.environ.get('WKHTMLTOPDF_PATH', None)
        if path:
            config = pdfkit.configuration(wkhtmltopdf=path)
        else:
            config = pdfkit.configuration()
        self.config = config


    def _options(self):
        opts = {
            '--print-media-type': None,
            '--disable-javascript': None,
            '--quiet': None,
            '--custom-header-propagation': None
        }

        return opts

    def convert(self, content, view=None):
        item = IPDFHTMLProvider(content)
        html = item.pdf_html(view=view)
        out = pdfkit.from_string(html, 
            False, 
            options=self._options(), 
            configuration=self.config
        )
        return StringIO(out)
