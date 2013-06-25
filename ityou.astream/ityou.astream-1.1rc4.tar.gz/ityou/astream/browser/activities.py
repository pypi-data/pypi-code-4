# -*- coding: utf-8 -*-
import logging
import time
from datetime import datetime, timedelta, date
import json

try:
    from BeautifulSoup import BeautifulSoup as bs
except ImportError:
    from bs4 import BeautifulSoup as bs

from stripogram import html2text

from Acquisition import aq_inner

from zope.interface import implements
from zope.component import getUtility
from zope.app.component.hooks import getSite

from plone.memoize.instance import memoize
from plone.outputfilters.browser.resolveuid import uuidToObject, uuidFor
from plone.registry.interfaces import IRegistry

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from ityou.astream.interfaces import IAstreamSettings

from .. import _
from .. import getWhoIsOnlineDBApi as WhoDBApi
from .. import isProductAvailable

from ..config import MESSAGE_TEXT_CONTAINER, TIME_STRING, MIN_ASTREAM_DELAY
from ..dbapi import DBApi

db = DBApi()


class ActivitiesView(BrowserView):
    """View of Activities
    """
    
    html_template = ViewPageTemplateFile('templates/activities.pt')
    
    def __call__(self):
        
        context = aq_inner(self.context)
        au = ActivityUtils()
        context.REQUEST.set('action', 'activities')
        self.site = getSite()
        
        ru =  getUtility(IRegistry)
        # *1000: transform milliseconds to seconds
        # We put this value in the Portlet DOM so that
        # jquery can fetch it
        # if value lower than MIN_ASTREAM_DELAY,
        # we take MIN_ASTREAM_DELAY
        self.ASTREAM_DELAY = max([ru.forInterface(IAstreamSettings).astream_delay*1000, MIN_ASTREAM_DELAY])
        self.ESI_ROOT = self.site.absolute_url() 
        
        # TODO -> 1.2
        self.user_astream = False
        self.separate_streams = False

        return self.html_template()


    def get_activities(self,max_activities=10,max_comments=200,au_id=None):
        """ Read activities out of the Database
        returns a dict with follow keys:
          user_id (int)
          md5
          user_name
          user_email
          content_uid
          content title
          content path
          message (text)
          comments (???)
          timestamp (DateTime) 
        """    
        context = aq_inner(self.context)

        ##ToDo --- #LM
        ##uid = context.REQUEST.get('uid')

        acts = db.getActivities(context=context, user_id=au_id, max=max_activities)
        au = ActivityUtils()
        p_acts = au._permission_activities(acts)
        activities = au.convertActivitiesForTemplate(context, p_acts)
                
        logging.debug("\n====> ACTIVITIES\n\t\t\t%s" % str(activities))
        return activities                               
            
class AjaxActivitiesView(BrowserView):
    """View of an Activity Stream loaded by AJAX and JQ
    """
    
    amount = db.countActivities()

    def __call__(self):
        """
        """
        context = aq_inner(self.context)
        request = context.REQUEST
        
        action =    request.form.get('action')
        timestamp = request.form.get('timestamp')        
        uid =       request.form.get('uid')
                
        if action == "get_latest_activities":
            return self.get_latest_activities(uid, timestamp)
        elif action == "get_more_activities":
            return self.get_more_activities(uid, timestamp)
        elif action == "get_latest_comments":
            return self.get_latest_comments(timestamp)
        else:
            pass
        
        return None 
            
    
    def get_latest_activities(self, uid, timestamp):
        """ Read activities out of the Database
        returns a dict with following keys:
          user_id (int)
          md5
          user_name
          user_email
          content_uid
          content title
          content path
          message (text)
          comments (???)
          timestamp (DateTime) 
        """
            
        context = aq_inner(self.context)
                    
        # ==== search new activities ===================================
        # 1. Check if there are new activities
        #    that are not yet displayed in the browser!
        #    - read Timesstamp of the latest activity
        #      from the request 
        #    - generate select: new timestamp > latest timestamp
        # 2. Send activities back as JSON Obj.
        # --------------------------------------------------------------
        
        if timestamp:
            acts = db.getActivities(context=context, user_id=uid, timestamp=timestamp)
        else:
            acts = db.getActivities(context=context, user_id=uid, max=5)
       
        au = ActivityUtils()
        p_acts = au._permission_activities(acts)
        activities = au.convertActivitiesForTemplate(context, p_acts)

        return au.jsonResponce(context, activities)


    def get_more_activities(self, uid, timestamp):
        """ Read activities out of the Database
        """
        context = aq_inner(self.context)
        acts = db.getActivities(context=context, user_id=uid, timestamp=timestamp, newer=False, max=5)       
        au = ActivityUtils()
        p_acts = au._permission_activities(acts)
        activities = au.convertActivitiesForTemplate(context, p_acts)
        return au.jsonResponce(context, activities)

        
    def get_latest_comments(self, timestamp):
        """ Read comments out of the Database
        returns a dict with following keys:
          user_id (int)
          user_name
          user_email
          comment
          timestamp (DateTime)
          md5 
        """
            
        context = aq_inner(self.context)
        cos = db.getComments(timestamp=timestamp, newer=True)
       
        au = ActivityUtils()
        comments = au.convertCommentsForTemplate(context, cos)

        return au.jsonResponce(context, comments)


class AjaxPostCommentView(BrowserView):
    """View for the comment posts
    Returns an activity_comment dict as json
    """

    def __call__(self):
        
        context = aq_inner(self.context)
        request = context.REQUEST
        mt      = getToolByName(context,"portal_membership")
        
        user      = mt.getAuthenticatedMember()
        user_id   = user.getId()
        user_name = user.getProperty('fullname').decode('utf-8')

        au = ActivityUtils()                
        portrait  = au.getPersonalPortrait(user_id, size='pico').absolute_url()        

        comment_txt = request.get("comment").replace("\n","[LF]")         
        comment = {
                'activity_md5': request.get('hash'),   
                'user_id':      user_id,      
                'user_name':    user_name,
                'user_email':   user.getProperty('email').decode('utf-8'),
                'portrait':     portrait,
                'comment':      html2text(comment_txt).replace("[LF]","\n").decode('utf-8'),
                'site_url':     getSite().absolute_url()
            }

        latest_comment = db.getLatestActivityComment(comment['activity_md5'])        
        timeout = datetime.now() - timedelta(seconds=120)

        who_db = WhoDBApi()
        try:
            if who_db: 
                self._track_whoisonline()
                        
            if (latest_comment['user_id'] == comment['user_id']) and (latest_comment['timestamp'] > timeout):                
                comment_confirm = db.updateComment(latest_comment['md5'],comment)
            else:
                comment_confirm = db.addComment(comment)
        except:
            comment_confirm = db.addComment(comment)
                            
        md5 = comment_confirm['md5']
        timestamp = datetime.strptime(comment_confirm['timestamp'], '%Y-%m-%d %H:%M:%S.%f')
        
        comment['hash']      = md5
        comment['timestamp'] = comment_confirm['timestamp']
        comment['timestr']   = timestamp.strftime(TIME_STRING)
        comment['comment']   = comment_txt.replace('[LF]','\n')

        return au.jsonResponce(context, comment)

    def _track_whoisonline(self):
        """ if WhoIsOnline is loaded, activity comments will be tracked, 
        """
        
        context = aq_inner(self.context)        
        mt = getToolByName(context,"portal_membership")
        user = mt.getAuthenticatedMember()

        who_db = WhoDBApi()
        who_db.addOnlineUser({
               "user_id":   user.getId(),
               "email":     user.getProperty("eamil",""),
               "doc_path":  context.absolute_url()            
        })
        return True

class AstreamPostActivity(BrowserView):
    """ Called by Javascript when sending an activity
    """

    def __call__(self):
        #if not getUtility(IRegistry).forInterface(IAstreamSettings).allow_user_activities:
        return False
        context = aq_inner(self.context)
        request = context.REQUEST
        mt = getToolByName(context, "portal_membership")
        auth_member = mt.getAuthenticatedMember()
        
        a = {
            "user_id"         : auth_member.getId().decode("utf-8"),
            "user_name"       : auth_member.getProperty("fullname").lstrip(" ").decode("utf-8"),
            "user_email"      : auth_member.getProperty("email").decode("utf-8"),
            "content_uid"     : u"",
            "content_title"   : u"",
            "content_path"    : u"",
            "message"         : request.get("a").decode("utf-8"),
            'site_url':         getSite().absolute_url()
             }
        
        try:
            db.addActivity(a)
            return True
        except:
            return False      

class ActivityUtils():
    """small utils
    """
    def _permission_content(self,acts):
        """ Returns only content to the user that he/she
        is allowed to see
        """        
        return [ uuidToObject(a['content_uid']) for a in acts ]
    
    def _permission_activities(self, acts):
        """ Display only activities which are linked to
        documents the the user is allowed to see
        """
        return  [ a for a in acts if uuidToObject(a['content_uid']) or a['content_uid'] == ""  ]
    

    def convertActivitiesForTemplate(self, context, acts):
        """Prepares activities to be displayed in the Template
        """        
        mt      = getToolByName(context,'portal_membership')
                
        activities = []
                       
        for a in acts:
            user_id  = a['user_id']                 
            content  = uuidToObject(a['content_uid'])

            if not content and a['content_uid'] != "":
                continue
            
            elif content:
                content_url     = content.absolute_url()
                if a['content_title']:
                    content_title  = a['content_title']
                    if MESSAGE_TEXT_CONTAINER.has_key(a['message']):
                        message = _(MESSAGE_TEXT_CONTAINER[a['message']], mapping = {"name": content_title})
                    else:
                        message = _(MESSAGE_TEXT_CONTAINER.get('undefined'), mapping = {"name": content_title})
                else:
                    content_title  = content.title_or_id()
                    message = _(MESSAGE_TEXT_CONTAINER.get('create'), mapping = {"name": content_title})            
            else:
                content_uid = None
                content_title = None
                content_url = None
                message = a['message']

            # Translation: use ___context____!!!: context.translate
            message = context.translate(message)
            
            au = ActivityUtils()
            portrait = au.getPersonalPortrait(user_id, size="pico").absolute_url()
            timestr = a['timestamp'].strftime(TIME_STRING)
            catalog = getToolByName(context, 'portal_catalog')
            try:
                result  = catalog({'UID' : a['content_uid']})
                obj = result[0].getObject()
                portal_type = obj.portal_type
            except:
                portal_type = None
                           
            a_tmpl = {
              "user_id":        user_id, 
              "portrait":       portrait,              
              "user_name":      a['user_name'],
              "user_email":     a['user_email'],  
              "content_title":  content_title,
              "content_url":    content_url,
              "content_uid":    a['content_uid'],
              "message":        message,
              "hash":            a['md5'],
              "timestr":        timestr,
              "timestamp":      str(a['timestamp']),         
              'site_url':       getSite().absolute_url(),
              'portal_type':    portal_type
            }
            
            comments = []
            for c in a['comments']:
                user_id     = c['user_id']
                user_name   = c['user_name']                    
                portrait = au.getPersonalPortrait(user_id, size="icon").absolute_url()
                timestr = c['timestamp'].strftime(TIME_STRING)
                
                c_tmpl = {
                    'user_id':      user_id,
                    'user_name':    user_name,
                    'user_email':   c['user_email'],
                    'comment':      c['comment'],
                    'timestamp':    str(c['timestamp']),
                    'timestr':      timestr,    
                    'portrait':     portrait,                
                    'hash':         c['md5'],
                    'site_url':     getSite().absolute_url() 
                }
                comments.append(c_tmpl)

            a_tmpl['comments'] = comments 
            
            activities.append(a_tmpl)                
                        
        return activities

    def convertCommentsForTemplate(self, context, cos):
        """Prepares comments to be rendered in a jquery-Template
        """
        mt       = getToolByName(context,'portal_membership')
        au       = ActivityUtils()        
        comments = []
        
        for c in cos:
            comments = []            
            user_id   = c.user_id
            user_name = c.user_name                    
            portrait  = au.getPersonalPortrait(user_id, size="icon").absolute_url()
            timestr   = c.timestamp.strftime(TIME_STRING)
            
            c_tmpl = {
                'user_id':      user_id,
                'user_name':    user_name,
                'user_email':   c.user_email,
                'comment':      c.comment,
                'timestamp':    str(c.timestamp),
                'timestr':      timestr,    
                'portrait':     portrait,                
                'hash':         c.md5,
                'activity_hash': c.activity_md5,
                'site_url':     getSite().absolute_url()               
            }
            
            comments.append(c_tmpl)
                                    
        return comments

    def jsonResponce(self, context, data):
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

    @memoize    
    def getSmallPortrait(self,portrait,username,size="small-personal-portrait"):
        """ rermoves width and height attributes
            and adds a class to the img tag
            if jquery is rendering the image, we only need
            the src of the image
        """
        
        soup = bs(portrait)
        img = soup.img

        return str(img['src'])

    @memoize
    def getPersonalPortrait(self,id=None, verifyPermission=0, size=None):
        """Adapts the original getPersonalPortrait 
        If ityou.extpersonalportrait is installed, the
        patched personal portrai will be called, else the
        default
        """
        plone = getSite()
        mt = getToolByName(plone,"portal_membership")
        if isProductAvailable('ityou.extuserprofile'):
            return mt.getPersonalPortrait(id, size=size)
        else:
            return mt.getPersonalPortrait(id=id)
    


