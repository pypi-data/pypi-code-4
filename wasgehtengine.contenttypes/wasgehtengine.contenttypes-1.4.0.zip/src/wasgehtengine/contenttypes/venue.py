# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from five import grok
from plone.app.textfield import RichText
from plone.directives import form
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.indexer.decorator import indexer
from plone.memoize.instance import memoize
from plone.uuid.interfaces import IUUID
from wasgehtengine.contenttypes import WasgehtengineMessageFactory as _
from z3c.form import button, validator, converter, interfaces
from z3c.relationfield.schema import RelationList, RelationChoice, RelationList, \
    RelationChoice
from zope import schema
from zope.component import getMultiAdapter, adapts
from zope.interface import Invalid, implements
from plone.memoize import ram
from datetime import datetime, timedelta
from zope.i18n import format
from urlparse import urlparse

def get_venue_type(venue):
        
    if venue.osm_element_tags is None:
        return None
        
    tags = venue.osm_element_tags
        
    if 'tourism' in tags and tags['tourism'] == 'museum':
        return 'museum'
    
    if 'shop' in tags and tags['shop'] == 'kiosk':
        return 'kiosk'
    
    if 'amenity' in tags:
        return tags['amenity']
        
    return None

# We need to specify own data converter in order to be able to
# input values with more than 3 fractions (for lon/lat).
# See http://old.nabble.com/Decimal-validation-error.-td27533964.html
class IGeoPosition(schema.interfaces.IFloat): 
    """Specify custom decimal interface"""
    
class GeoPosition(schema.Float):
    implements(IGeoPosition)
 
class GeoPositionDataConverter(converter.FloatDataConverter): 
    """Adapt float data converter""" 
    adapts(GeoPosition, interfaces.IWidget) 
    # The amount of '#' after the '.' outlines the no. of decimal places 
    pattern = '#,##0.################'
    
    def toFieldValue(self, value): 
        try:
            # call formatter.parse just to check if value
            # is a valid float value, otherwise NumberParseError is thrown
            self.formatter.parse(value, pattern=self.pattern)
            
            # but do real conversion in order to prevent
            # field value to be a broken number like 54.3422343234e+15
            return round(float(value), 7)
        except format.NumberParseError, err: 
            raise converter.FormatterValidationError(self.errorMessage, value)   

class IVenue(form.Schema):
    """A venue
    """

    website = schema.URI(
                title=_("Website"),
                description=_("Venue's website"),
                required=False,
            )
    
    latitude = GeoPosition(
                title=_("Latitude"),
                description=_("Latitude"),
                required=False,
                )

    longitude = GeoPosition(
                title=_("Longitude"),
                description=_("Longitude"),
                required=False,
                )
    
    form.omitted('osm_element_id')
    osm_element_id = schema.Int(
                title=_("OSM Element ID"),
                description=_("OSM Element ID"),
                required=False,
            )

    form.omitted('osm_element_type')
    osm_element_type = schema.Choice(
                title=_("OSM Element Type"),
                description=_("OSM Element Type"),
                required=False,
                values=["Node", "Way", "Relation"],
            )
    
    form.omitted('osm_element_tags')
    osm_element_tags = schema.Dict(
                title=_("OSM Element Tags"),
                description=_("OSM Element Tags"),
                required=False,
                key_type=schema.TextLine(title=_("Key")),
                value_type=schema.TextLine(title=_("Value")),
            )

    form.omitted('postal_address')
    postal_address = schema.Dict(
                title=_("Postal Address"),
                description=_("Postal Address of the venue"),
                required=False,
                key_type=schema.TextLine(title=_("field")),
                value_type=schema.TextLine(title=_("Value")),
            )

    phone_number = schema.ASCIILine(
                title=_("Phone Number"),
                description=_("Phone number"),
                required=False,
                )

class View(grok.View):
    """Default view (called "@@view"") for a venue.

    The associated template is found in venue_templates/view.pt.
    """

    grok.context(IVenue)
    grok.require('zope2.View')
    grok.name('view')

    def update(self):
        pass
    
    def upcoming_events(self):
        return self.events_after((datetime.today() - timedelta(days=1)).date(), venue='/'.join(self.context.getPhysicalPath()))
    
    def upcoming_screenings(self):
        return self.screenings_after((datetime.today() - timedelta(days=1)).date(), venue='/'.join(self.context.getPhysicalPath()))
        
    # cache this function until change    
    #@ram.cache(lambda method, self, start, venue: (start, venue))
    def events_after(self, start, venue):
        catalog = getToolByName(self.context, 'portal_catalog')
        results = catalog.searchResults(portal_type='wasgehtengine.Event', period_start={ "query": [start, ], "range": "min" }, venue=venue)
        
        return sorted([brain.getObject() for brain in results], key=lambda event: event.start)
    
    def screenings_after(self, start, venue):
        catalog = getToolByName(self.context, 'portal_catalog')
        results = catalog.searchResults(portal_type='wasgehtengine.Screening', period_start={ "query": [start, ], "range": "min" }, venue=venue)
        
        return sorted([brain.getObject() for brain in results], key=lambda screening: screening.start)
    
    
    def get_event_import_status(self): 
        catalog = getToolByName(self.context, 'portal_catalog')
        
        results = catalog.searchResults(portal_type='wasgehtengine.EventImportStatus', venue='/'.join(self.context.getPhysicalPath()))
        
        if results == None or len(results) == 0:
            return None
        
        return results[0].getObject()
    
    def venue_type(self):
        return get_venue_type(self.context)
        
@indexer(IVenue)
def website(context):
    if not hasattr(context, 'website'):
        return None
    
    if not context.website:
        return None
    
    url = urlparse(context.website)
    
    return str(url.netloc)
    
grok.global_adapter(website, name="website")

@indexer(IVenue)
def venue_type(context):
        
    if not context.osm_element_tags:
        return None

    if 'tourism' in context.osm_element_tags:
        if context.osm_element_tags['tourism'] == 'museum':
            return 'museum'

    if 'shop' in context.osm_element_tags:
        if context.osm_element_tags['shop'] == 'kiosk':
            return 'kiosk'

    if 'amenity' in context.osm_element_tags:
        return context.osm_element_tags['amenity']

grok.global_adapter(venue_type, name="venue_type")