# -*- coding: utf-8 -*-
from django.conf.urls import url, patterns

from .views import ContactFormView


urlpatterns = patterns(
    '',
    # Contact with a pre-defined rule
    url(r'^subject/(?P<subject>[-\w]+)/$', ContactFormView.as_view(),
        name='contact_form_rule'),

    # Contact a registered user (by a slug)
    url(r'^(?P<slug>[-\w]+)/$', ContactFormView.as_view(),
        name='user_contact_form_by_slug'),

    # Contact a registered user (by its pk)
    url(r'^user/(?P<pk>\d+)/$', ContactFormView.as_view(),
        name='user_contact_form_by_pk'),

    # Default contact form
    url(r'^$', ContactFormView.as_view(), name='contact_form'),
)
