from django.conf.urls import patterns, url, include
from ci.views import TriggerTest
from viewsets import ViewSet

defaultpatterns = patterns(r'^ci/', include("ci.urls"))

urlpatterns = ViewSet.all_urls()

urlpatterns += patterns('',
    url(r'^trigger/(?P<name>[^/]+)/(?P<branch>[\-\_\w]+)/', TriggerTest.as_view()),
)
