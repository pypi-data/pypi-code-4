from django.conf.urls import patterns, url

urlpatterns = patterns('template_pages.views',
    url(r'^(?P<path>[^.\n]*)/$', 'routing_view', name='template_pages_routing_view'),
    url(r'^$', 'routing_view', {'path':''}, name='template_pages_routing_view'),
)
