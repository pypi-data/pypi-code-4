from django.conf.urls.defaults import *

urlpatterns = patterns('sirep.views',
    # Reports list
    url('^$', 'reports_list', name='sirep.reports_list'),

    # HTML report
    url('^(?P<slug>.*)/$', 'view_report', name='sirep.view_report'),

    # CSV report
    url('^csv/(?P<slug>.*)$', 'view_csv_report', name='sirep.view_csv'),
)
