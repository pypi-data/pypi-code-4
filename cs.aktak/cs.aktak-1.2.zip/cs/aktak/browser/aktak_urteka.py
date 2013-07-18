from Acquisition import aq_inner
from Products.Five.browser import BrowserView

class AktakUrteka(BrowserView):
    def __call__(self):
        context = self.context
        return Aktak(context, self.request).items()

class Aktak(BrowserView):
    
    def items(self):        
        context = aq_inner(self.context)
        urteak = context.getFolderContents({'portal_type':'DonEdukia'})
        dict = {}
        for urtea in urteak:
            aktak = urtea.getObject().getFolderContents({'portal_type':'File'}, full_objects=1)
            dict[urtea.Title] = aktak

        return dict
