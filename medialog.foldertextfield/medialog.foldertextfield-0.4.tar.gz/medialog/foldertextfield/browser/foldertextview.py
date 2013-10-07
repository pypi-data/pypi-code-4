from zope.interface import implements, alsoProvides, noLongerProvides
from zope.interface import implements, Interface
#from Products.Five.utilities.marker import mark
from ..interfaces import IFolderTextObject


from Products.Five import BrowserView
 
class IFolderTextView(Interface):
    """
    Folder view interface
    """

    def test():
        """ test method"""
    
    
class FolderTextView(BrowserView):
    """
    Folder view
    """
    implements(IFolderTextView)
    
    def test(self):
        """
        test method
        """
        dummy = _(u'a dummy string')

        return {'dummy': dummy}



class IFolderTextEnable(Interface):
    """
    Toggle Folder textfield interface
    """

    def __call__():
        """ toggle text field method"""
        

class FolderTextEnable(BrowserView):
    """
    Toggle Folder text field
    """
    implements(IFolderTextEnable)
    
    def __call__(self):
        """
        toggle textfield
        """
        
        #mark(self, IFolderTextEnable)
        
        
        if not IFolderTextObject.providedBy(self.context):
            alsoProvides(self.context, IFolderTextObject)
            self.context.reindexObject(idxs=['object_provides'])
            self.request.response.redirect(self.context.absolute_url())
            
        else:  
            noLongerProvides(self.context, IFolderTextObject)
            self.context.reindexObject(idxs=['object_provides'])
            if self.context.getLayout() == 'foldertext_view' :
            	self.context.setLayout('folder_listing')
            self.request.response.redirect(self.context.absolute_url())