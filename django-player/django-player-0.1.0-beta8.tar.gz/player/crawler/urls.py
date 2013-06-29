from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('player.crawler.views',
    url(r'^$', 'report_index', name='report_index'),
    url(r'^report/(?P<report_id>\w+)/$', 'report_view', name='report_view'),
    url(r'^report/(?P<report_id>\w+)/crawled_data/$', 'crawled_view', name='crawled_view'),
)
