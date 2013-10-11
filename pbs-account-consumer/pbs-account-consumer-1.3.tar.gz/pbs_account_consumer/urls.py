from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'pbs_account_consumer.views',
    url(r'^login/$', 'login_begin', name='login_begin'),
    url(r'^login/immediate/$', 'login_begin', {'immediate': True},
        name='login_begin_immediate'),
    url(r'^complete/$', 'login_complete'),
    url(r'^setup_needed/$', 'setup_needed', name='login_setup_needed'),
    url(r'^change_password/$', 'change_password'),
    url(r"^change_password/complete$", "ax_change_complete")
)
