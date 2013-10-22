# -*- coding: utf-8 -*-
"""
Url's map "racine"
"""
from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin

admin.autodiscover()

from Sveetchies.django.documents.views.page import HelpPage, PageIndex, PageDetails, PageSource

urlpatterns = patterns('',
    url(r'^$', PageDetails.as_view(), {'slug':"accueil"}, name='documents-homepage'),
    
    # Admin
    #(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
    
    (r'^board/', include('Sveetchies.django.documents.urls_board')),
    (r'^djangocodemirror-sample/', include('Sveetchies.django.djangocodemirror.urls')),
    
    url(r'^documents-help/$', HelpPage.as_view(), name='documents-help'),
    url(r'^sitemap/$', PageIndex.as_view(), name='documents-index'),
    
    url(r'^(?P<slug>[-\w]+)/$', PageDetails.as_view(), name='documents-page-details'),
    url(r'^(?P<slug>[-\w]+)/source/$', PageSource.as_view(), name='documents-page-source'),
)
        
# En production (avec le debug_mode à False) ceci ne sera pas chargé
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^medias/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    )
