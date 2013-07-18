from zope.interface import Interface, implements
from zope.component import queryMultiAdapter

from Acquisition import aq_inner
from Products.Five.browser import BrowserView


class INavigationRootContent(Interface):
    def section_content_body_class():
        pass


class NavigationRootContent(BrowserView):
    implements(INavigationRootContent)

    def section_content_body_class(self):
        portal_state = queryMultiAdapter((self.context, self.request),
                                         name='plone_portal_state')
        navigation_root_path = portal_state.navigation_root_path()
        root_path_length = len(navigation_root_path)
        path_name = '-'.join(self.context.getPhysicalPath())[root_path_length:]
        if path_name != '-':
            return 'content-section' + path_name
        else:
            return ''

