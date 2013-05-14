# -*- coding: utf-8 -*-
from plone.memoize.instance import memoize
from Products.CMFCore.utils import getToolByName 
from Acquisition import aq_inner
from zope.app.component.hooks import getSite


class WhoIsOnlineUtils:
    
    def who_is_online_list(self):
        """ Returns list of Online Users
        """
        #TODO
        who_is_online_list = []
        return who_is_online_list


class WhoAmIUtils:
    
    @memoize
    def user_profile(self,context,show_all):
        """ Returns the user profile as a dict
        """
        # show_all not used
        mt      = getToolByName(context,'portal_membership')
        
        user    = mt.getAuthenticatedMember()        
        user_id = user.getId()

        image   = mt.getPersonalPortrait(user_id).getTagName()
        portrait_url = mt.getPersonalPortrait(user_id).absolute_url()

        user_fullname= u""        
        # if ityou.extuserprofile is installed #todo
        if not user.getProperty('fullname'):
            user_fullname =  "%s %s" % (user.getProperty('firstname',''), user.getProperty('lastname',''))
            if user.getProperty("acadtitle",''):
                user_fullname = "%s %s"  % (user.getProperty("acadtitle",''), user_fullname)
        else:
            user_fullname = user.getProperty('fullname')
        try:
            user_data = {
                'id'          : user_id,                              
                'fullname'    : user_fullname,
                'email'       : user.getProperty('email'),
                'profile'     : getSite().absolute_url() + '/author/' + user_id,
                'home'        : mt.getHomeUrl(user_id, verifyPermission=1),
                'portrait'    : portrait_url,
                 }
        except: #TODO
            user_data = None
        
        return user_data
    
