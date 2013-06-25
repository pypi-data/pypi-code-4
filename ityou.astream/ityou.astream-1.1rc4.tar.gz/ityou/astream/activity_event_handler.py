# -*- coding: utf-8 -*-
import logging
from five import grok
from datetime import datetime

from Products.CMFCore.interfaces import IActionSucceededEvent
from Products.ATContentTypes.interfaces.interfaces import IATContentType
from zope.lifecycleevent.interfaces import IObjectModifiedEvent, IObjectCopiedEvent, IObjectCreatedEvent
from Products.CMFEditions.Permissions import AccessPreviousVersions
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import IFolderish
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from ityou.astream.interfaces import IAstreamSettings
from .dbapi import DBApi
from . import getNotifyDBApi
db = DBApi()

@grok.subscribe(IATContentType, IObjectModifiedEvent)
def ContentModifyEventHandler(context,event):
    """Content Modified
    """
    request     = context.REQUEST
    user        = request.get('AUTHENTICATED_USER')
    
    if not IFolderish.providedBy(context):
        message = request.get('fieldname')
        if not message:
            utils = Utils()
            message = utils.create_or_edit(context)
            
        activity = {
          "user_id":            user.getId(),
          "user_name":          user.getProperty('fullname','').lstrip(' ').decode('utf-8'),
          "user_email":         user.getProperty('email',''),
          "content_uid":        context.UID(),  
          "content_title":      context.Title().decode('utf-8'),
          "content_path":       '/'.join(context.getPhysicalPath()).decode('utf-8'),
          "message":            message,
        }
        activity_md5 = db.addActivity(activity)
        notice = request.get('cmfeditions_version_comment')
        
        if notice:
            comment = {
                "activity_md5":     activity_md5,
                "user_id":          user.getId(),
                "user_name":        user.getProperty('fullname','').lstrip(' ').decode('utf-8'),
                "user_email":       user.getProperty('email',''),
                "comment":          notice.decode('utf-8'),
                       }
            db.addComment(comment)
        
        notify_dbapi = getNotifyDBApi()
        if notify_dbapi:
            notify_dbapi.addNotification({
                "action":           u'astream',
                "sender_id":        activity['user_id'],
                "sender_name":      activity['user_name'],
                "sender_email":     activity['user_email'],
                "content_uid":      activity["content_uid"],
                "content_path":     activity["content_path"],
                "content_title":    activity["content_title"],
                "message":          activity["message"],
                "timestamp_mod":    datetime.now(),
                 })        
                #"content_path":     activity["content_path"].decode("utf-8"),#warum hier decode??
    return None
   
@grok.subscribe(IATContentType, IActionSucceededEvent)
def ActivityStreamWorkflowLogging(context,event):
    """ Workflow state change
    """
    return None

class Utils():
    def create_or_edit(self,context):
        if not _checkPermission(AccessPreviousVersions, context):
            return "undefined"

        rt = getToolByName(context, "portal_repository", None)
        if rt is None or not rt.isVersionable(context):
            return "undefined"

        context_url = context.absolute_url()
        history=rt.getHistoryMetadata(context)
        if history.getLength(context) == 1:
            return "create"
        else:
            return "edit"

