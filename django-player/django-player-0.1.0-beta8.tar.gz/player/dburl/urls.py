from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('player.dburl.views',
    url(r'^$', 'url_list', name='url_list'),
    url(r'^add/$', 'url_add', name='url_add'),
    url(r'^(?P<url_id>\d+)/$', 'url_detail', name='url_detail'),
    url(r'^(?P<url_id>\d+)/edit/$', 'url_edit', name='url_edit'),
)
