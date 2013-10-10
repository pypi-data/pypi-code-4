from django.conf.urls import patterns, include, url

urlpatterns = patterns('remotestatus.views',
    url(r'^remote-box/(?P<remote_box_id>[0-9]+)/$', 'remote_box_detail', name='rs-remote-box-detail'),
    url(r'^(?P<call_round_id>[0-9]+)/$', 'dashboard', name='rs-dashboard'),
    url(r'^$', 'dashboard', name='rs-dashboard'),
)