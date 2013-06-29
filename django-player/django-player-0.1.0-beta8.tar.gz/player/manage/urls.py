from django.conf.urls.defaults import patterns, include, url


urlpatterns = patterns('',
    (r'^$', 'player.manage.views.index'),
    url(r'^generic_delete/$', 'player.manage.views.generic_delete', name='generic_delete'),
    url(r'^content_delete/$', 'player.manage.views.content_delete', name='content_delete'),
    (r'^block/', include('player.block.urls')),
    (r'^crawler/', include('player.crawler.urls')),
    (r'^data/', include('player.data.urls')),
    (r'^dbtemplates/', include('player.dbtemplate.urls')),
    (r'^dburls/', include('player.dburl.urls')),
    (r'^staging/', include('player.player_staging.urls')),
    url(r'^login/$', 'django.contrib.auth.views.login', name="auth_login"),
    url(r'^logout/$', 'django.contrib.auth.views.logout', name="auth_logout"),
    url(r'^inlinetrans/', include('inlinetrans.urls')),
)
