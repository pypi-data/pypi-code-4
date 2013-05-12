# -*- coding: utf-8 -*-

import zope.interface

from Products.Five.browser import BrowserView
from Products.PloneboardNotify.interfaces import ILocalBoardNotify

class PloneboardNotificationSystemView(BrowserView):
    """View for managing Ploneboard notification system in control panel"""
    
    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        request.set('disable_border', True)
        
    def __call__(self):
        request = self.request
        if request.form.get("pbn_save"):
            self._updateConfiguration(request.form)
            request.response.redirect(self.context.absolute_url()+"/@@ploneboard_notification")
        return self.index()
    
    def _resetLocalConfiguration(self):
        """Remove no more used properties from the context"""
        context = self.context
        context.manage_delProperties(['forum_sendto_values','forum_sendto_all'])
        # zope.interface.noLongerProvides(context, ILocalBoardNotify) # Do not use until Plone 2.5 support will be dropped
        zope.interface.directlyProvides(context, zope.interface.directlyProvidedBy(context)-ILocalBoardNotify)
        
    def _addNeededProperties(self, context):
        """Add the properties forum_sendto_values and forum_sendto_all if not existings"""
        if not context.hasProperty('forum_sendto_values'):
            context.manage_addProperty('forum_sendto_values', [], 'lines')
        if not context.hasProperty('forum_sendto_all'):
            context.manage_addProperty('forum_sendto_all', False, 'boolean')        

    def _updateConfiguration(self, form):
        """Update saved configuration data"""
        context = self.context
        sendto_values = [x.strip() for x in form.get("sendto_values").replace("\r","").split("\n") if x]
        if form.get("sendto_all"):
            sendto_all = True
        else:
            sendto_all = False
        if not sendto_all and not sendto_values:
             # Empty values remove properties AND the provided interface
            self._resetLocalConfiguration()
        else:
            zope.interface.directlyProvides(context, ILocalBoardNotify)
            self._addNeededProperties(context)
            context.manage_changeProperties(forum_sendto_values=sendto_values,
                                            forum_sendto_all=sendto_all)

    def load_sendto_values(self):
        """Load the local forum_sendto_values value"""
        context = self.context
        return "\n".join(context.getProperty('forum_sendto_values', []))

    def load_sendto_all(self):
        """Load the sendto_all value"""
        context = self.context
        return context.getProperty('forum_sendto_all', False)



