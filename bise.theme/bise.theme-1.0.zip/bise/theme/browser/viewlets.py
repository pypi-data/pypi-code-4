from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.layout.viewlets import common
from Acquisition import aq_base, aq_inner
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName

class LogoViewlet(common.LogoViewlet):
    index = ViewPageTemplateFile('logo.pt')
    def update(self):
        super(LogoViewlet, self).update()

        portal = self.portal_state.portal()
        bprops = portal.restrictedTraverse('base_properties', None)
        if bprops is not None:
            logoName = 'BiseLogo.png'
        else:
            logoName = 'BiseLogo.png'
        logoTitle = self.portal_state.portal_title()
        self.logo_tag = portal.restrictedTraverse(logoName).tag(title=logoTitle, alt=logoTitle, itemprop="logo")
        self.navigation_root_title = self.portal_state.navigation_root_title()

class PersonalBarViewlet(common.PersonalBarViewlet):

    index = ViewPageTemplateFile('personal_bar.pt')

    def update(self):
        super(PersonalBarViewlet, self).update()
        self.home = self.portal_state.navigation_root_url()
        self.about = '/'.join([self.portal_state.navigation_root_url(), "info"])
        self.sitemap = '/'.join([self.portal_state.navigation_root_url(), "sitemap"])

class PathBarViewlet(common.PathBarViewlet):
    index = ViewPageTemplateFile('path_bar.pt')



class GlobalSectionsViewlet(common.GlobalSectionsViewlet):
    index = ViewPageTemplateFile('sections.pt')

    def update(self):
        context = aq_inner(self.context)
        portal_tabs_view = getMultiAdapter((context, self.request),
                                           name='portal_tabs_view')
        self.portal_tabs = []
        pps = getMultiAdapter((self.context, self.request), name='plone_portal_state')
        portal = pps.portal()
        for tab in portal_tabs_view.topLevelTabs():
            tab['navmenucode'] = u''
            tab_obj = portal.get(tab['id'], None)
 	    if tab_obj:
                if hasattr(tab_obj, 'navmenucode'):
                    tab['navmenucode'] = tab_obj.navmenucode and tab_obj.navmenucode.output or ''
	    self.portal_tabs.append(tab)
#        self.portal_tabs = portal_tabs_view.topLevelTabs()

        self.selected_tabs = self.selectedTabs(portal_tabs=self.portal_tabs)
        self.selected_portal_tab = self.selected_tabs['portal']

    def selectedTabs(self, default_tab='index_html', portal_tabs=()):
        plone_url = getToolByName(self.context, 'portal_url')()
        plone_url_len = len(plone_url)
        request = self.request
        valid_actions = []

        url = request['URL']
        path = url[plone_url_len:]
        for action in portal_tabs:
            if not action['url'].startswith(plone_url):
                # In this case the action url is an external link. Then, we
                # avoid issues (bad portal_tab selection) continuing with next
                # action.
                continue
            action_path = action['url'][plone_url_len:]
            if not action_path.startswith('/'):
                action_path = '/' + action_path
            if path.startswith(action_path + '/') or path == action_path:
                # Make a list of the action ids, along with the path length
                # for choosing the longest (most relevant) path.
                valid_actions.append((len(action_path), action['id']))


        # Sort by path length, the longest matching path wins
        valid_actions.sort()
        if valid_actions:
            return {'portal' : valid_actions[-1][1]}

        return {'portal' : default_tab}
