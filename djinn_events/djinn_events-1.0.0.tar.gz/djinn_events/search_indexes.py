from haystack import site
from djinn_events.models.event import Event
from pgsearch.base import ContentRealTimeSearchIndex


class EventIndex(ContentRealTimeSearchIndex):

    """ Index for events """


site.register(Event, EventIndex)
