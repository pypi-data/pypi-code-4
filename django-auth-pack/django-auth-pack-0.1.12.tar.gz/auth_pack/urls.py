from django.conf.urls import patterns, url
from auth_pack.views import ajax_login, ajax_registration, activate, registration_complete, activate_complete, ChangePasswordView
from auth_pack.views import password_reset, password_reset_confirm, password_done, password_reset_done


def auth_pack_urls(params={}):
    return patterns('',
        url(r'login/$', ajax_login, params.get('login', {}),
            name='login'),
        url(r'registration/complete/$', registration_complete, params.get('registration_complete', {}),
            name='registration_complete'),
        url(r'registration/$', ajax_registration, params.get('registration', {}),
            name='registration'),
        url(r'activate/complete/$', activate_complete, params.get('activate_complete', {}),
            name='activate_complete'),
        url(r'activate/(?P<activation_key>\w+)/$', activate, name='activate'),
        url(r'changepass/$', ChangePasswordView.as_view(**params.get('changepass', {})),
            name='change_password'),
        url(r'logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='logout'),
        url(r'password/reset/$', password_reset, params.get('password_reset', {}),
            name='password_reset'),
        url(r'password/reset/done/$', password_reset_done, params.get('password_reset_done', {})),
        url(r'password/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
            password_reset_confirm, params.get('password_reset_confirm', {})),
        url(r'password/done/$', password_done),
    )
