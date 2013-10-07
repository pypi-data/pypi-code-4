from copy import deepcopy
import datetime

from django.conf.urls.defaults import *

urlpatterns = patterns('nano.blog.views',
        (r'^(?P<year>\d{4})/(?P<month>[01]\d)/(?P<day>[0123]\d)/$', 'list_entries_by_date'),
        (r'^(?P<year>\d{4})/(?P<month>[01]\d)/$', 'list_entries_by_year_and_month'),
        (r'^(?P<year>\d{4})/$',     'list_entries_by_year'),
        (r'^latest/$',              'list_latest_entries'),
        (r'^today/$',               'list_entries_for_today'),
        (r'^$',                     'list_entries'),
)
