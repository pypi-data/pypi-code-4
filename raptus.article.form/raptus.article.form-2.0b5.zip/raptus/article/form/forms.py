from zope import interface, component

from Products.CMFCore.utils import getToolByName

from Products.PloneFormGen.interfaces import IPloneFormGenForm

from raptus.article.core.interfaces import IArticle
from raptus.article.form.interfaces import IForms

class Forms(object): 
    """ Provider for forms contained in an article
    """
    interface.implements(IForms)
    component.adapts(IArticle)
    
    def __init__(self, context):
        self.context = context
        
    def getForms(self, **kwargs):
        """ Returns a list of forms (catalog brains)
        """
        catalog = getToolByName(self.context, 'portal_catalog')
        return catalog(object_provides=IPloneFormGenForm.__identifier__, path={'query': '/'.join(self.context.getPhysicalPath()),
                                                                               'depth': 1}, sort_on='getObjPositionInParent', **kwargs)
