from five import grok
from zope import schema
from plone.directives import form

from plone.app.textfield import RichText

from wasgehtengine.contenttypes.venue import IVenue
from Products.CMFCore.utils import getToolByName

from zope.component import getUtility
from zope.component import getMultiAdapter
from zope.container.interfaces import INameChooser

from zope.lifecycleevent.interfaces import IObjectAddedEvent

from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping

from Acquisition import aq_parent
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.publisher.browser import BrowserView
from zope.interface import implements
from zope.viewlet.interfaces import IViewlet
from zope.viewlet.interfaces import IViewletManager
from venue import get_venue_type

class IVenueFolder(form.Schema):
    """A folder that can contain venues 
    """
    pass

class View(grok.View):
    """Default view (called "@@view"") for a venue folder.
    
    The associated template is found in venuefolder_templates/view.pt.
    """
    
    grok.context(IVenueFolder)
    grok.require('zope2.View')
    grok.name('view')
    
    def update(self):
        pass
    
class IVenueFolderViewlet(BrowserView):
    implements(IViewlet)
    
    render = ViewPageTemplateFile('venuefolder_templates/venuefolder_viewlet.pt')

    def update(self):
        for id, item in [('', self.context)] + self.context.contentItems():     
           if IVenueFolder.providedBy(item):
               self.venuefolder = item
               return
           
    def venues(self):

        catalog = getToolByName(self.context, 'portal_catalog')
        
        requested_venue_groups = self.request.get('venue_type', [])
                        
        results = catalog.searchResults(path=dict(query='/'.join(self.venuefolder.getPhysicalPath()),
                                          depth=1), portal_type='wasgehtengine.Venue', venue_type={
                                            "query": requested_venue_groups,
                                            "operator" : "or" })
        
        venue_groups = {}
        
        for brain in results:
            venue = brain.getObject()
            venue_type = get_venue_type(venue)
            
            if venue_type is None:
                continue
            
            if not venue_type in venue_groups:
                venue_groups[venue_type] = []
            
            venue_groups[venue_type].append(venue)
                
        return venue_groups
    
class IVenueFolderViewletManager(IViewletManager):
    """A viewlet manager...
    """