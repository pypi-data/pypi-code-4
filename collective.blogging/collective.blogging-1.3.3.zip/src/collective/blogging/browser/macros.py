from zope.interface import implements

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.blogging.interfaces import IBloggingView

class BlogMacros(BrowserView):
    """ Helper macros view """
    
    implements(IBloggingView)
    
    template = ViewPageTemplateFile('blog_macros.pt')
    
    @property
    def macros(self):
        return self.template.macros

class EntryMacros(BrowserView):
    """ Helper macros view """
    
    implements(IBloggingView)
    
    template = ViewPageTemplateFile('entry_macros.pt')
    
    @property
    def macros(self):
        return self.template.macros
