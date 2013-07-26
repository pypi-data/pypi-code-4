from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'pbs_account_consumer.views',
    url(r'^login/$', 'login_begin', name='login_begin'),
    url(r'^complete/$', 'login_complete'),
)
