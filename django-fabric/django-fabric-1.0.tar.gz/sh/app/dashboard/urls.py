# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

urlpatterns = patterns('sh.app.dashboard.views',
    url(r'^$', 'view_dashboard', name='view_dashboard'),
)