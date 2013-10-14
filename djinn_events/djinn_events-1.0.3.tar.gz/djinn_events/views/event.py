from djinn_contenttypes.views.base import DetailView
from djinn_contenttypes.utils import urn_to_object
from djinn_events.models import Event


class EventView(DetailView):

    model = Event

    @property
    def link(self):

        _link = (self.object.link or "").split("::")[0]
        
        if _link.startswith("urn"):
            return urn_to_object(_link).get_absolute_url()
        else:
            return _link

    @property
    def link_target(self):
        try:
            return (self.object.link or "").split("::")[1]
        except:
            return None

    @property
    def link_title(self):

        _link = (self.object.link or "").split("::")[0]

        if _link.startswith("urn"):
            return urn_to_object(self.object.link).title
        else:
            return _link
