# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url
from .views import callback, sync, progress, download

urlpatterns = patterns('',
    url(r'^callback/$',
        callback,
        name='viddler_callback'),
    url(r'^sync/$',
        sync,
        name='viddler_sync'),
    url(r'^download/(?P<videoid>.+)/$',
        download,
        name='viddler_download'),
    url(r'^progress/$',
        progress,
        name='viddler_progress'),
)
