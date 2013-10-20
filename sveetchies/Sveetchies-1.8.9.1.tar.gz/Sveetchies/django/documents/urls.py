# -*- coding: utf-8 -*-
"""
Url's map "racine"
"""
from django.conf.urls.defaults import *

from Sveetchies.django.documents.views.page import HelpPage, PageIndex, PageDetails, PageSource

urlpatterns = patterns('',
    url(r'^$', PageIndex.as_view(), name='documents-index'),
    
    (r'^board/', include('Sveetchies.django.documents.urls_board')),
    
    url(r'^sitemap/$', PageIndex.as_view(), name='documents-index'),
    url(r'^documents-help/$', HelpPage.as_view(), name='documents-help'),
    
    url(r'^(?P<slug>[-\w]+)/$', PageDetails.as_view(), name='documents-page-details'),
    url(r'^(?P<slug>[-\w]+)/source/$', PageSource.as_view(), name='documents-page-source'),
)
