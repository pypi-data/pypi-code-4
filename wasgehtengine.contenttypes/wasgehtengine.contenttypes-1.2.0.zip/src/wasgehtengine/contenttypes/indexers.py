from five import grok
from plone.indexer import indexer
from venue import IVenue
from event import IEvent
from DateTime import DateTime
from urlparse import urlparse

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