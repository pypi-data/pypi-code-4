from djinn_events.models.event import Event
from haystack import indexes
from pgsearch.base import ContentSearchIndex


class EventIndex(ContentSearchIndex, indexes.Indexable):

    def get_model(self):

        return Event
