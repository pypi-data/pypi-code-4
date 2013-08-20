from django.conf.urls import patterns, url, include
from django.contrib import admin
admin.autodiscover()

from .views import TimelineDetailView, TimelineListView, ImportTimelineFromSpreadsheetView

urlpatterns = patterns('',
    url(r'^$', TimelineListView.as_view(), name='timelines'),
    url(r'^import/$', ImportTimelineFromSpreadsheetView.as_view(), name='import_timeline_from_spreadsheet'),
    # this is for tests, you probably want to remove this or use your own urls.py
    url(r'^admin/', include(admin.site.urls)),
    url(r'^(?P<slug>[a-zA-Z0-9-_]+)/$', TimelineDetailView.as_view(), name='timeline'),
)
