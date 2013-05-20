from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
import datetime
from django.utils.translation import ugettext as _
from events.models import EventsPlugin as EventsPluginModel
from events.models import Event


class EventsPlugin(CMSPluginBase):
    model = EventsPluginModel
    name = _("Events")
    render_template = "events/plugin.html"
    module = _("TheHerk")

    def render(self, context, instance, placeholder):
        events = Event.objects.filter(end__gte=datetime.date.today()).order_by('start')[:instance.number_to_show]
        context.update({
            'instance': instance,
            'events': events,
            'placeholder': placeholder,
        })
        return context

plugin_pool.register_plugin(EventsPlugin)
