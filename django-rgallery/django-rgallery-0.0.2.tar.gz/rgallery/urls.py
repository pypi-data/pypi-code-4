# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from rgallery.views import Photos, Videos

urlpatterns = patterns('',
    url(r'^$',                              Photos.as_view(), {}, 'app_gallery-gallery'),
    url(r'^page/(?P<page>\d+)/$',           Photos.as_view(), {}, 'app_gallery-gallery-page'),
    url(r'^videos/$',                       Videos.as_view(), {}, 'app_gallery-videos'),
    url(r'^videos/page/(?P<page>\d+)/$',    Videos.as_view(), {}, 'app_gallery-videos-page'),
)
