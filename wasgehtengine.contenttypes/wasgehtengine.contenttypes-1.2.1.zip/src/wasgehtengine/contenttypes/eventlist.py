# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from five import grok
from plone.app.textfield import RichText
from plone.directives import form
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.memoize.instance import memoize
from plone.uuid.interfaces import IUUID
from venue import IVenue
from wasgehtengine.contenttypes import WasgehtengineMessageFactory as _
from z3c.form import validator
from z3c.relationfield.schema import RelationList, RelationChoice, RelationList, \
    RelationChoice, Relation
from zope import schema
from zope.component import getMultiAdapter
from zope.interface import Invalid
from plone.app.layout.navigation.interfaces import INavigationRoot
from DateTime import DateTime
from datetime import timedelta
from datetime import datetime
import iso8601

class DayView(grok.View):
    """List all events for one day

    The associated template is found in eventlist_templates/dayview.pt.
    """

    grok.context(INavigationRoot)
    grok.require('zope2.View')
    grok.name('dayview')

    def update(self):
        day_iso_str = self.request.form['day']
        
        self.day = iso8601.parse_date(day_iso_str+'T05:00:00Z') if day_iso_str else datetime.today() - timedelta(hours=5)
    
    def events(self):
            
        start = DateTime(self.day.isoformat())
        
        catalog = getToolByName(self.context, 'portal_catalog')
        
        end = start + 1
        
        print("Start: " + str(start))
        print("End: " + str(end))
        
        results = catalog.searchResults(portal_type='wasgehtengine.Event', period_start={ "query": [start, end],
                         "range": "minmax" })
        
        return [brain.getObject() for brain in results]
    
    def previous(self):
        return self.url() + '?day=' + (self.day - timedelta(days=1)).strftime("%Y-%m-%d") 
    
    def next(self):
        return self.url() + '?day=' + (self.day + timedelta(days=1)).strftime("%Y-%m-%d") 