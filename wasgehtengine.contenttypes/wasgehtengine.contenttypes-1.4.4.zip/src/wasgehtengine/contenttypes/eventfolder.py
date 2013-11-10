from five import grok
from zope import schema
from plone.directives import form

from wasgehtengine.contenttypes.event import IEvent
from Products.CMFCore.utils import getToolByName

from zope.component import getUtility
from zope.component import getMultiAdapter
from zope.container.interfaces import INameChooser

from zope.lifecycleevent.interfaces import IObjectAddedEvent

from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping

from Acquisition import aq_parent

from DateTime import DateTime
from datetime import timedelta
from datetime import datetime
import iso8601
import locale

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.publisher.browser import BrowserView
from zope.interface import implements
from zope.viewlet.interfaces import IViewlet
from zope.viewlet.interfaces import IViewletManager
from plone.memoize import ram

class IEventFolder(form.Schema):
    """A folder that can contain events 
    """
    pass

class View(grok.View):
    """Default view (called "@@view"") for a event folder.
    
    The associated template is found in eventfolder_templates/view.pt.
    """
    
    grok.context(IEventFolder)
    grok.require('zope2.View')
    grok.name('view')
    
    def update(self):
        pass
    
class IEventFolderViewlet(BrowserView):
    implements(IViewlet)
    
    render = ViewPageTemplateFile('eventfolder_templates/eventfolder_viewlet.pt')

    def update(self):

        self.day = iso8601.parse_date(self.request.form['day']+'T05:00:00Z') if 'day' in self.request.form else (datetime.today() - timedelta(hours=5)).replace(hour=5,minute=0)
        
        for id, item in [('', self.context)] + self.context.contentItems():     
            if IEventFolder.providedBy(item):
                self.eventfolder = item
                return
                
    def datestring(self):
        locale.setlocale(locale.LC_ALL, '')
        
        if self.day.date() == (datetime.today() - timedelta(hours=5)).date():
            return 'Heute (' + self.day.strftime('%A, %x') + ')'
        
        if self.day.date() == (datetime.today() - timedelta(hours=5)).date() + timedelta(1):
            return 'Morgen ('  + self.day.strftime('%A, %x') + ')'
        
        return self.day.strftime('%A, %x')
    
    def previous(self):
        return self.eventfolder.absolute_url() + '?day=' + (self.day - timedelta(days=1)).strftime("%Y-%m-%d") 
    
    def next(self):
        return self.eventfolder.absolute_url() + '?day=' + (self.day + timedelta(days=1)).strftime("%Y-%m-%d")
    
    def events(self):
            
        start = DateTime(self.day.isoformat())
        
        end = start + 1
                
        return self.events_for_range(start, end)
    
    # cache this function until change    
    #@ram.cache(lambda method, self, start, end: (start, end))
    def events_for_range(self, start, end):
        catalog = getToolByName(self.context, 'portal_catalog')
        results = catalog.searchResults(path=dict(query='/'.join(self.eventfolder.getPhysicalPath()),
                                          depth=1), portal_type='wasgehtengine.Event', period_start={ "query": [start, end],
                         "range": "minmax" })
        
        return [brain.getObject() for brain in results]

class IEventFolderViewletManager(IViewletManager):
    """A viewlet manager...
    """