from djinn_events.models.event import Event
from pgsearch.base import ContentSearchIndex


class EventIndex(ContentSearchIndex):

    def get_model(self):

        return Event
