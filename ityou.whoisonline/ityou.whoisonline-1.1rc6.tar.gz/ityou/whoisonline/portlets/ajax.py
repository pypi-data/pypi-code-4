# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser import BrowserView

from Products.CMFCore.utils import getToolByName 
from zope.component import getUtility
from Acquisition import aq_inner
from zope.app.component.hooks import getSite
from plone.registry.interfaces import IRegistry
from datetime import datetime, timedelta, date
import logging
import json


from operator import itemgetter
from plone.memoize.instance import memoize

from ..interfaces import IWhoIsOnlineSettings
from ..dbapi import DBApi
from .. import _
from .. import db_imessage, ityou_extuserprofile_installed
from ..config import TIME_STRING

db  = DBApi()

#TIME_STRING = _(u"%d.%m.%Y um %H:%M:%S Uhr")

class UserProfile():
    """Defines the userprofile
    """
    id          = u""                              
    fullname    = u"" 
    email       = u"" 
    profile     = u""
    home        = u""
    portrait    = u""
    recent_path = u""
    recent_doc  = u""
    recent_time = u""
    bar         = u""
    
class AjaxWhoIsOnlineView(BrowserView):
    """AJAX list of online users 
    """
        
    template = ViewPageTemplateFile('whoisonline-ajax.pt')
    
    def __call__(self):

        context = aq_inner(self.context)
        request = context.REQUEST
        request.set('disable_border', True)
        wu = WhoIsOnlineUtils()

        action = request.get('action')
        user_id = request.get('user_id')
        
        if action == "show_userprofile":
            user_profile = self.user_profile(user_id)            
            return user_profile
        elif action == "show_onlineusers":
            online_users = self.online_users()
            return online_users        
        else:
            return self.template()

        
    def online_users(self):
        """ get the short profile of users
        """
        online_users = []        
        context = aq_inner(self.context)
        request = context.REQUEST

        ru =  getUtility(IRegistry)
        timeout_online = ru.forInterface(IWhoIsOnlineSettings).timeout_online
        ou =  db.getOnlineUsers(timeout_online)
        if ou:
            online_users = self._convert_online_users(ou)

        # remote json-request?
        if request.get('callback',''):
            wu = WhoIsOnlineUtils()
            return wu.jsonResponse(context,online_users)
        else:
            return online_users
        
    def user_profile(self, user_id):
        """ get the profile of a single user
        """                 
        user_profile = {}
        context = aq_inner(self.context)
        request = context.REQUEST

        ru =  getUtility(IRegistry)
        timeout_online = ru.forInterface(IWhoIsOnlineSettings).timeout_online        
        up =  db.getUserProfile(timeout_online,user_id)
        if up:
            user_profile = self._convert_user_profile(up)
    
        wu = WhoIsOnlineUtils()
        return wu.jsonResponse(context,user_profile)


    def _convert_user_profile(self,ou):

        context = aq_inner(self.context)
        request = context.REQUEST
                
        mt = getToolByName(context,'portal_membership')
        user_id = mt.getAuthenticatedMember().getId()
        
        ru =  getUtility(IRegistry)
        timeout_online = ru.forInterface(IWhoIsOnlineSettings).timeout_online
        
        user_profile = {}

        now_timestamp = int(datetime.now().strftime('%s'))
        
        if user_id !=  ou['user_id']:
            user = mt.getMemberById(ou['user_id'])

            # --- bar = 0 - 100  / auf 1.00 normiert---               
            delta = datetime.now() - ou["timestamp"]
            bar   = round(  ( float(timeout_online - delta.seconds ) / timeout_online ) , 1)
            
            image = mt.getPersonalPortrait(ou['user_id']).getTagName()
            if image != "Image":
                portrait_url = mt.getPersonalPortrait(ou['user_id']).absolute_url()
            else: # ToDo
                portrait_url = mt.getPersonalPortrait(ou['user_id']).absolute_url()

            user_fullname = user.getProperty('fullname') or user.getId()
            
            profile     = getSite().absolute_url() + '/author/' + ou['user_id'],
            home        = mt.getHomeUrl(ou['user_id'], verifyPermission=1) or profile
            
            user_profile = {
                          'id'          : ou['user_id'],                              
                          'fullname'    : user_fullname,
                          'email'       : user.getProperty('email'),
                          'profile'     : profile,
                          'home'        : home,
                          'portrait'    : portrait_url,
                          'recent_path' : ou["doc_path"],
                          'recent_doc'  : ou["doc_path"].split('/')[-1],
                          'recent_time' : ou["timestamp"].strftime(TIME_STRING),
                          'bar'         : bar
                          }
        return user_profile
        
                        
    def _convert_online_users(self,online_users):

        context = aq_inner(self.context)
        request = context.REQUEST
                
        mt = getToolByName(context,'portal_membership')
        user_id = mt.getAuthenticatedMember().getId()

        ru =  getUtility(IRegistry)
        timeout_online = ru.forInterface(IWhoIsOnlineSettings).timeout_online
        max_users = ru.forInterface(IWhoIsOnlineSettings).max_users
        
        
        users = []
        for ou in online_users:
            
            now_timestamp = int(datetime.now().strftime('%s'))
            
            if user_id !=  ou['user_id']:

                user = mt.getMemberById(ou['user_id'])
                # --- bar = 0 - 100  / auf 1.00 normiert---               
                delta = datetime.now() - ou["timestamp"]
                bar   = round(  ( float(timeout_online - delta.seconds ) / timeout_online ) , 1)
                
                image = mt.getPersonalPortrait(ou['user_id']).getTagName()
                if ityou_extuserprofile_installed:
                    portrait_url = mt.getPersonalPortrait(ou['user_id'], size='icon').absolute_url()
                else:
                    portrait_url = mt.getPersonalPortrait(ou['user_id']).absolute_url()
                users.append({
                              'id'          : ou['user_id'],                              
                              'profile'     : getSite().absolute_url() + '/author/' + ou['user_id'],
                              'portrait'    : portrait_url,
                              'bar'         : bar
                              })
        
        return users[:max_users]


    def imessage_installed(self):
        if db_imessage:
            return True
        else:
            return False
    
    

class AjaxWhoIsOnlineTrigger(BrowserView):
    """AJAX Trgger for whoisonline 
    """
        
    def __call__(self):
        """Triggers WhoIsOnline
        """
        context = aq_inner(self.context)        
        mt = getToolByName(context,"portal_membership")
        user = mt.getAuthenticatedMember()
         
        if user.getId():
            # ==== write to DB =========        
            db.addOnlineUser({
               "user_id":   user.getId(),
               "email":     user.getProperty("eamil",""),
               "doc_path":  context.absolute_url()
            })
            
        wu = WhoIsOnlineUtils() 
        return wu.jsonResponse(context, { 'user_id' : user.getId()} )

class WhoIsOnlineUtils():
    """small utils"""

    def jsonResponse(self, context, data):
        """ Returns Json Data in Callback function
        """
        request = context.REQUEST
        callback = request.get('callback','')        
        request.response.setHeader("Content-type","application/json")
        if callback:
            cb = callback + "(%s);"
            return cb % json.dumps(data)
        else:
            return json.dumps(data)

