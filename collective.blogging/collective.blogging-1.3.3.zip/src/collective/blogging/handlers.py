from Products.CMFCore.utils import getToolByName
from collective.blogging.interfaces import IBlogMarker, IEntryMarker

def initBlogLayout(obj, event):
    """ Set blog layout if bloggable object is created with the blogging markup """
    
    if IBlogMarker.providedBy(obj):
        obj.setLayout('blog-view')

def updateBlogLayout(obj, event):
    """ Reset blog layout if modified bloggable object hasn't the blogging markup"""
    
    if not IBlogMarker.providedBy(obj):
        if obj.getLayout() == 'blog-view':
            ptypes = getToolByName(obj, 'portal_types')
            type_info = ptypes.getTypeInfo(obj.portal_type)
            obj.setLayout(type_info.default_view)
        

def initEntryLayout(obj, event):
    """ Set entry layout if postable object is created with the blogging markup """
    
    if IEntryMarker.providedBy(obj):
        obj.setLayout('entry-view')

def updateEntryLayout(obj, event):
    """ Reset entry layout if modified postable object hasn't the blogging markup"""
    
    if not IEntryMarker.providedBy(obj):
        if obj.getLayout() == 'entry-view':
            ptypes = getToolByName(obj, 'portal_types')
            type_info = ptypes.getTypeInfo(obj.portal_type)
            obj.setLayout(type_info.default_view)
