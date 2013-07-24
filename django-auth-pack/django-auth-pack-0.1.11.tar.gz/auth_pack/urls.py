from django.conf.urls import patterns, url
from auth_pack.views import ajax_login, ajax_registration, activate, registration_complete, activate_complete, ChangePasswordView
from auth_pack.views import password_reset, password_reset_confirm, password_done, password_reset_done


default_params = dict(
    login={},
    registration={},
    registration_complete={},
    activation_complete={},
    changepass={},
    password_reset={},
    password_reset_done={},
    password_reset_confirm={},
)


def auth_pack_urls(params):
    params = default_params.update(params)
    return patterns('',
        url(r'login/$', ajax_login, params.login,
            name='login'),
        url(r'registration/complete/$', registration_complete, params.registration_complete,
            name='registration_complete'),
        url(r'registration/$', ajax_registration, params.registration,
            name='registration'),
        url(r'activate/complete/$', activate_complete, params.activate_complete,
            name='activate_complete'),
        url(r'activate/(?P<activation_key>\w+)/$', activate, name='activate'),
        url(r'changepass/$', ChangePasswordView.as_view(**params.changepass),
            name='change_password'),
        url(r'logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='logout'),
        url(r'password/reset/$', password_reset, params.password_reset,
            name='password_reset'),
        url(r'password/reset/done/$', password_reset_done, params.password_reset_done),
        url(r'password/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
            password_reset_confirm, params.password_reset_confirm),
        url(r'password/done/$', password_done),
    )
