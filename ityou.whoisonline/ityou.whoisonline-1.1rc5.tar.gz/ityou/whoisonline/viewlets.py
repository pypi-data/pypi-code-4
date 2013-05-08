# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName 
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase    


from .dbapi import DBApi
db  = DBApi()

class OnlineTrackingViewlet(ViewletBase):
    """Checks who is online and writes log to database
    """
    
    def update(self):
        super(OnlineTrackingViewlet, self).update()
                  
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
                
    index =  ViewPageTemplateFile('whoisonline-tracking.pt')
    
