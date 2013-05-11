from django.conf.urls.defaults import *

urlpatterns = patterns('sirep.views',
    url('^$', 'reports_list', name='sirep.reports_list'),
    # Report URLs
    url('^(?P<slug>.*)/$', 'view_report', name='sirep.view_report'),
    url('^csv/(?P<slug>.*)$', 'view_csv_report', name='sirep.view_csv'),
)
