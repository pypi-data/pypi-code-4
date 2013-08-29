from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five import BrowserView

class HelpView(BrowserView):
    """ A help browser view """

    template = ViewPageTemplateFile('help.pt')
    
    def __call__(self):
        self.request.set('disable_border', True)
        return self.template()
