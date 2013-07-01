from zope import interface, component

from Products.CMFCore.utils import getToolByName

from raptus.article.core.interfaces import IArticle
from raptus.article.additionalwysiwyg.interfaces import IWYSIWYG

class WYSIWYG(object): 
    """ Provider for an additional WYSIWYG text of an article
    """
    interface.implements(IWYSIWYG)
    component.adapts(IArticle)
    
    def __init__(self, context):
        self.context = context
        
    def getAdditionalText(self):
        """ Returns the additional WYSIWYG text
        """
        return self.context.Schema()['additional-text'].get(self.context)
