# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from Products.Ploneboard.interfaces import IPloneboard, IForum
from Products.PloneboardNotify.interfaces import ILocalBoardNotify

class PloneboardNotificationSystemView(BrowserView):
    """View for managing Ploneboard notification system in control panel"""
    
    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        request.set('disable_border', True)
        self.portal_properties = getToolByName(context, 'portal_properties')
        
    def __call__(self):
        request = self.request
        if request.form.get("pbn_save"):
            self._updateConfiguration(request.form)
            request.response.redirect(self.context.absolute_url()+"/@@ploneboard_notification")
        return self.index()
    
    def _updateConfiguration(self, form):
        """Update saved configuration data"""
        ploneboard_notify_properties = self.portal_properties['ploneboard_notify_properties']
        sendto_values = [x.strip() for x in form.get("sendto_values").replace("\r","").split("\n") if x]
        if form.get("sendto_all"):
            sendto_all = True
        else:
            sendto_all = False
        ploneboard_notify_properties.sendto_all = sendto_all
        ploneboard_notify_properties.sendto_values = sendto_values

    @property
    def portal_boards(self):
        """Perform a catalog search for all ploneboard objects in the portal"""
        # BBB: get rid of object_implements as soon as Plone 2.5 support will be dropped
        catalog = getToolByName(self.context, 'portal_catalog')
        return catalog(object_provides=IPloneboard.__identifier__,
                       object_implements=IPloneboard.__identifier__,
                       sort_on='sortable_title')

    @property
    def orphan_forums(self):
        """Get all forums that are not contained inside message board content types"""
        catalog = getToolByName(self.context, 'portal_catalog')
        forums = catalog(object_provides=IForum.__identifier__,
                         object_implements=IForum.__identifier__,
                         sort_on='sortable_title')
        orphans = []
        for forum in forums:
            path = forum.getPath()
            board = catalog(path={'query': path[:path.rfind('/')],
                                  'depth': 0},
                            object_provides=IPloneboard.__identifier__,
                            object_implements=IPloneboard.__identifier__,)
            if not board:
                orphans.append(forum)
        return orphans

    def getForums(self, area_brain):
        """Return all forums inside the area forum passed"""
        catalog = getToolByName(self.context, 'portal_catalog')
        return catalog(object_provides=IForum.__identifier__,
                       object_implements=IForum.__identifier__,
                       path=area_brain.getPath()
                       )

    def isLocalEnabled(self, forum_brain):
        """Check is the Forum use local configuration, so if provides ILocalBoardNotify"""
        forum = forum_brain.getObject()
        return ILocalBoardNotify.providedBy(forum)

    def load_sendto_values(self):
        """Load the global ploneboard_notify_properties value"""
        return "\n".join(self.portal_properties['ploneboard_notify_properties'].sendto_values)
    
    def load_sendto_all(self):
        """Load the sendto_all value"""
        return self.portal_properties['ploneboard_notify_properties'].sendto_all


