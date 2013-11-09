from five import grok
from zope import schema
from plone.directives import form

from wasgehtengine.contenttypes.screening import IScreening
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
import difflib

class IScreeningFolder(form.Schema):
    """A folder that can contain movie screenings 
    """
    pass

class View(grok.View):
    """Default view (called "@@view"") for a screening folder.
    
    The associated template is found in screeningfolder_templates/view.pt.
    """
    
    grok.context(IScreeningFolder)
    grok.require('zope2.View')
    grok.name('view')
    
    def update(self):
        pass
    
class IScreeningFolderViewlet(BrowserView):
    implements(IViewlet)
    
    render = ViewPageTemplateFile('screeningfolder_templates/screeningfolder_viewlet.pt')

    def update(self):
        self.day = iso8601.parse_date(self.request.form['day']+'T05:00:00Z') if 'day' in self.request.form else (datetime.today() - timedelta(hours=5)).replace(hour=5,minute=0)
        
        for id, item in [('', self.context)] + self.context.contentItems():     
            if IScreeningFolder.providedBy(item):
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
    
    def get_movie_group(self, movie_title, movie_groups):
        
        # first case, the movie title already has a group, so just use it.
        if movie_title in movie_groups:
            return movie_title
        
        # second case, a similar movie name already exists, then use that.
        movie_group = difflib.get_close_matches(movie_title, movie_groups.keys(), 1, 0.8)
            
        if movie_group:
            return movie_group[0]
        
        return movie_title
    
    def screenings(self):
            
        start = DateTime(self.day.isoformat())
        
        end = start + 1
                
        screenings = self.screenings_for_range(start, end)
        
        screenings_by_movie_by_start = {} 
        
        for screening in screenings:
            
            movie_group = self.get_movie_group(screening.movie_title, screenings_by_movie_by_start)
            
            if not movie_group in screenings_by_movie_by_start:
                screenings_by_movie_by_start[movie_group] = {}
                
            if not screening.start.replace(second=0,microsecond=0) in screenings_by_movie_by_start[movie_group]:
                screenings_by_movie_by_start[movie_group][screening.start.replace(second=0,microsecond=0)] = []
                
            screenings_by_movie_by_start[movie_group][screening.start.replace(second=0,microsecond=0)].append(screening)

        return screenings_by_movie_by_start
    
    # cache this function until change    
    #@ram.cache(lambda method, self, start, end: (start, end))
    def screenings_for_range(self, start, end):
        catalog = getToolByName(self.context, 'portal_catalog')
        results = catalog.searchResults(path=dict(query='/'.join(self.eventfolder.getPhysicalPath()),
                                          depth=1), portal_type='wasgehtengine.Screening', period_start={ "query": [start, end],
                         "range": "minmax" })
        
        return [brain.getObject() for brain in results]

class IScreeningFolderViewletManager(IViewletManager):
    """A viewlet manager...
    """