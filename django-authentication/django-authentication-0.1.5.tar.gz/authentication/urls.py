# coding: utf8

from django.conf.urls import patterns, url
from django.conf import settings

from coreutils.loading import load_module

AuthenticationForm = load_module(getattr(
    settings,
    'AUTHENTICATION_LOGIN_FORM',
    'authentication.forms.AuthenticationForm'
))

from .views.activation import ActivatePage, ActivationCompletePage
from .views.registration import (
    RegistrationPage, RegistrationCompletePage, RegistrationClosedPage
)


def BuildAccountUrl(*url_suffixes):
    return r'^%s$' % '/'.join((
        (getattr(settings, 'ACCOUNT_URL_PREFIX', 'settings/account'),) +
        url_suffixes
    ))


urlpatterns = patterns('',
    url(BuildAccountUrl('password', 'change'),
        'django.contrib.auth.views.password_change', {
            'template_name': 'authentication/password_change_form.html',
        }, name='password_change'),
    url(BuildAccountUrl('password', 'change', 'done'),
        'django.contrib.auth.views.password_change_done', {
            'template_name': 'authentication/password_change_done.html',
        }, name='password_change_done'),

    url(r'^login$', 'django.contrib.auth.views.login', {
            'authentication_form': AuthenticationForm,
            'template_name': 'authentication/login.html',
        },
        name='login'),
    url(r'^logout$', 'django.contrib.auth.views.logout', {
            'template_name': 'authentication/logged_out.html',
        }, name='logout'),
)

if getattr(settings, 'ACCOUNT_ACTIVATION_ENABLED', True):
    urlpatterns += patterns('',
        url(r'^activate/complete$',
            ActivationCompletePage.as_view(),
            name='account_activation_complete'),
        url(r'^activate/(?P<activation_key>\w+)$',
            ActivatePage.as_view(),
            name='account_activate'),
    )

if getattr(settings, 'ACCOUNT_REGISTRATION_ENABLED', True):
    urlpatterns += patterns('',
        url(r'^signup$',
            RegistrationPage.as_view(),
            name='account_register'),
        url(r'^signup/complete$',
            RegistrationCompletePage.as_view(),
            name='account_registration_complete'),
        url(r'^signup/closed$',
            RegistrationClosedPage.as_view(),
            name='account_registration_disallowed'),
    )

if getattr(settings, 'ACCOUNT_PASSWORD_RESET_ENABLED', True):
    urlpatterns += patterns('',
        url(BuildAccountUrl('password', 'reset'),
            'django.contrib.auth.views.password_reset', {
                'template_name': 'authentication/password_reset_form.html',
            }, name='password_reset'),
        url(BuildAccountUrl('password', 'reset', 'done'),
            'django.contrib.auth.views.password_reset_done', {
                'template_name': 'authentication/password_reset_done.html',
            }, name='password_reset_done'),
        url(BuildAccountUrl('password', 'reset', '(?P<uidb36>[0-9A-Za-z]{1,13}'
                ')-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})'),
            'django.contrib.auth.views.password_reset_confirm', {
                'template_name': 'authentication/password_reset_confirm.html',
            }, name='password_reset_confirm'),
        url(BuildAccountUrl('password', 'reset', 'complete'),
            'django.contrib.auth.views.password_reset_complete', {
                'template_name': 'authentication/password_reset_complete.html',
            }, name='password_reset_complete'),
    )
