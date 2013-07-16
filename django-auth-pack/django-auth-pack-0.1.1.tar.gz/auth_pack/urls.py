from django.conf.urls import patterns, url
from auth_pack.views import ajax_login, ajax_registration, activate


def auth_pack_urls(login_params, registration_params):
    return patterns('',
        url(r'login/$', ajax_login, login_params, name='login'),
        url(r'registration/$', ajax_registration, registration_params, name='registration'),
        url(r'activate/(?P<activation_key>\w+)/$', activate, name='activate'),
        url(r'logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='logout'),
    )
