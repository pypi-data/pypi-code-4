from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('player.player_staging.views',
    url(r'^$', 'server_list', name='server_list'),
    url(r'^add/$', 'server_add', name='server_add'),
    url(r'^(?P<server_id>\d+)/$', 'server_detail', name='server_detail'),
    url(r'^(?P<server_id>\d+)/edit/$', 'server_edit', name='server_edit'),
    url(r'^publish/$', 'publish', name='publish'),
    url(r'^publish/new/$', 'publish_new', name='publish_new'),
    url(r'^publish/commit/$', 'commit', name='commit'),
    url(r'^create_repo_from_server/$', 'create_repo_from_server', name='create_repo_from_server'),
    url(r'^update_from_repository/$', 'update_from_repository', name='update_from_repository'),
    url(r'^log/$', 'log_view', name='log_view'),
    url(r'^log/(?P<changeset_id>[0-9a-f\:]+)/$', 'log_detail', name='log_detail'),
)
