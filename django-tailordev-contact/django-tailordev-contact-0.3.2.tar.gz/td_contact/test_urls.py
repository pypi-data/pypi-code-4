# -*- coding: utf-8 -*-
from django.conf.urls import include, patterns, url
from django.views.generic import TemplateView


urlpatterns = patterns(
    '',
    url(r'^$', TemplateView.as_view(template_name="_layouts/base.html"),
        name='home'),
    url(r'^contact/', include('td_contact.urls')),
)
