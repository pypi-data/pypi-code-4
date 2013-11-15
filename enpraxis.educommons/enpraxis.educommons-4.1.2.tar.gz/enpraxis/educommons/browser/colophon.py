from plone.app.layout.viewlets import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName


class eduCommonsColophonViewlet(ViewletBase):
    """ Viewlet for eduCommons """

    index = ViewPageTemplateFile('colophon.pt')

    def update(self):
        super(eduCommonsColophonViewlet, self).update()
        self.context_state = getMultiAdapter((self.context, self.request),
                                             name=u'plone_context_state')
        
    def isUserAnonymous(self):
        """Is the user anonymous or logged in?"""
        return self.portal_state.anonymous()

    def getActions(self):
        """Get colophon action information"""
        return self.context_state.actions('eccolophon_actions')
        
    def getVersion(self):
        """ Get the current version of eduCommons """
        qi = getToolByName(self.context, 'portal_quickinstaller')
        return qi.getProductVersion('enpraxis.educommons')

    def getUserName(self):
        """Get fullname of user and corresponding roles"""
        userid = self.portal_state.member().getId()
        ms = getToolByName(self.context, 'portal_membership')
        minfo = ms.getMemberInfo(userid)
        if minfo['fullname']:
            return minfo.get('fullname')
        return userid

    def getUserRoles(self):
        """Get user roles"""
        uroles = self.portal_state.member().getRoles()
        roles = [x for x in uroles if x not in ['Authenticated', 'Member']]
        if roles:
            return '(%s)' %(', '.join(roles))
        return None
        
        
