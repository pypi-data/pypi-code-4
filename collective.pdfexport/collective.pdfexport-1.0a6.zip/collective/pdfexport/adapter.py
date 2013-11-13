from collective.pdfexport.interfaces import IPDFHTMLProvider
from Products.CMFCore.interfaces import IContentish
from five import grok

class DefaultPDF(grok.Adapter):
    grok.context(IContentish)
    grok.implements(IPDFHTMLProvider)

    def pdf_html(self, view=None): 
        if view is None:
            return self.context()
        return self.context.restrictedTraverse(view)()

