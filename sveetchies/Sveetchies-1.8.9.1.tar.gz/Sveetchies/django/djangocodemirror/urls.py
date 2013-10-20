# -*- coding: utf-8 -*-
"""
Url's map for documents board
"""
from django.conf.urls.defaults import *

from Sveetchies.django.djangocodemirror.views import Sample, SamplePreview, SampleQuicksave

urlpatterns = patterns('',
    url(r'^$', Sample.as_view(), name='djangocodemirror-sample-view'),
    url(r'^preview/$', SamplePreview.as_view(), name='djangocodemirror-sample-preview'),
    url(r'^quicksave/$', SampleQuicksave.as_view(), name='djangocodemirror-sample-quicksave'),
)
