# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from five import grok
from plone.app.textfield import RichText
from plone.directives import form
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.indexer import indexer
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
from DateTime import DateTime
from datetime import datetime
from  zope.lifecycleevent.interfaces import IObjectCreatedEvent, IObjectAddedEvent

class IEvent(form.Schema):
    """An event
    """

    venue = RelationChoice(
                title=_("Venue"),
                description=_("Event's venue"),
                source=ObjPathSourceBinder(object_provides=IVenue.__identifier__),
                required=True,
            )

    website = schema.URI(
                title=_("Website"),
                description=_("Event's website"),
                required=False,
            )

    start = schema.Datetime(
                title=_("Start"),
                description=_("Start date/time"),    
                required=True,
            )

    end = schema.Datetime(
                title=_("End"),
                description=_("End date/time"),    
                required=False,
            )
    
    no_starttime = schema.Bool(
                title=_("No start time"),
                description=_("Whether a precise start time is given or not"),
                required=False,
                default=False,
    )
    
    no_endtime = schema.Bool(
                title=_("No end time"),
                description=_("Whether a precise end time is given or not"),
                required=False,
                default=False,                           
    )

class View(grok.View):
    """Default view (called "@@view"") for an event.

    The associated template is found in event_templates/view.pt.
    """

    grok.context(IEvent)
    grok.require('zope2.View')
    grok.name('view')

    def update(self):
        pass
    
    def autoimport_url(self):
        
        event_import_status = self.get_event_import_status()
        
        if event_import_status is not None:
            return event_import_status.absolute_url()
    
    def get_event_import_status(self): 
        catalog = getToolByName(self.context, 'portal_catalog')
        
        results = catalog.searchResults(portal_type='wasgehtengine.EventImportStatus', venue='/'.join(self.context.venue.to_object.getPhysicalPath()))
        
        if results == None or len(results) == 0:
            return None
        
        return results[0].getObject()
    
@indexer(IEvent)
def period_start_indexer(context):
    
    return DateTime(context.start.isoformat())

grok.global_adapter(period_start_indexer, name="period_start")

@indexer(IEvent)
def period_end_indexer(context):
    
    return DateTime(context.end.isoformat())

grok.global_adapter(period_end_indexer, name="period_end")

@indexer(IEvent)
def venue_indexer(context):    
    return str('/'.join(context.venue.to_object.getPhysicalPath()))

grok.global_adapter(venue_indexer, name="venue")