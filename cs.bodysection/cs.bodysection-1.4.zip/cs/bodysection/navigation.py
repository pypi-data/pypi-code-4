from zope.interface import Interface, implements
from zope.component import queryMultiAdapter
from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from plone.app.layout.navigation.root import getNavigationRootObject

class INavigationRootContent(Interface):
    def section_content_body_class():
        """ return a unique section class based on the id of the nearer child of a 
        INavigationRoot item parent of the current context
        """

class NavigationRootContent(BrowserView):
    implements(INavigationRootContent)

    def section_content_body_class(self):
        portal_state = queryMultiAdapter((self.context, self.request),
                                         name='plone_portal_state')

        context = aq_inner(self.context)
        portal = portal_state.portal
        navigation_root = getNavigationRootObject(context, portal)
        root_path_len = len(navigation_root.getPhysicalPath())
        current_path = context.getPhysicalPath()
        if len(current_path) > root_path_len:
            
            return 'content-section-' + current_path[root_path_len]
        else:
            return ''


        
        
        
