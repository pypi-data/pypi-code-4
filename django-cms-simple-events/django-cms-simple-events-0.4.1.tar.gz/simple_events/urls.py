from django.conf.urls import patterns, include, url
from models import Event

urlpatterns = patterns('',
    url(r'^$', 'simple_events.views.events', name='events'),
    url(r'^(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$',
            'simple_events.views.events_day', name="events_day"),
    url(r'^(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/(?P<slug>[-\w]+)/$',
            'simple_events.views.events_detail', name="events_detail"),
)
