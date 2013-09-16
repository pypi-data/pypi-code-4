"""Defaults urls for the Zinnia project"""
from django.conf.urls import url
from django.conf.urls import patterns
from django.views.generic.base import TemplateView
from .views import subscribe, unsubscribe

urlpatterns = patterns(
    '',
    url(r'^subscribe/$', subscribe, name='subscribe'),
    url(r'^unsubscribe/$', unsubscribe, name='unsubscribe'),
    url(r'^subscribe/success/$', TemplateView.as_view(
        template_name='cmsplugin_mailchimp/successful_subscription.html'),
        name='subscribe_success'),
    url(r'^subscribe/failure/$', TemplateView.as_view(
        template_name='cmsplugin_mailchimp/failed_subscription.html'),
        name='subscribe_failed'),
)
