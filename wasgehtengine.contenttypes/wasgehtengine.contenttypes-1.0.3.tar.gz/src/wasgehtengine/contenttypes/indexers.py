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
        
    if not hasattr(context, 'osmReference'):
        return None

    if not context.osmReference:
        return None

    if not hasattr(context.osmReference, 'osmElementTags'):
        return None

    if not context.osmReference.osmElementTags:
        return None

    if 'tourism' in context.osmReference.osmElementTags:
        if context.osmReference.osmElementTags['tourism'] == 'museum':
            return 'museum'

    if 'shop' in context.osmReference.osmElementTags:
        if context.osmReference.osmElementTags['shop'] == 'kiosk':
            return 'kiosk'

    if 'amenity' in context.osmReference.osmElementTags:
        return context.osmReference.osmElementTags['amenity']

grok.global_adapter(venue_type, name="venue_type")


@indexer(IEvent)
def period_start_indexer(context):
    if not hasattr(context, 'period'):
        return None
    
    if not context.period:
        return None
    
    return DateTime(context.period.start.isoformat())

grok.global_adapter(period_start_indexer, name="period_start")

@indexer(IEvent)
def period_end_indexer(context):
    if not hasattr(context, 'period'):
        return None
    
    if not context.period:
        return None
    
    return DateTime(context.period.end.isoformat())

grok.global_adapter(period_end_indexer, name="period_end")

@indexer(IEvent)
def venue_indexer(context):    
    return str('/'.join(context.venue.to_object.getPhysicalPath()))

grok.global_adapter(venue_indexer, name="venue")