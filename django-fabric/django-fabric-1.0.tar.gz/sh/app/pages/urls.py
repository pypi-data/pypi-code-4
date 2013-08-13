# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

urlpatterns = patterns('sh.app.pages.views',
    url(r'^$', 'view_page', name='view_page'),
    url(r'^add/$', 'edit_page', name='add_page'),
    url(r'^(?P<id>\d+)/edit/$', 'edit_page', name='edit_page'),
    url(r'^(?P<id>\d+)/delete/$', 'delete_page', name='delete_page'),
    url(r'^(?P<page_slug>[a-z0-9-_]+)/$', 'view_page', name='view_page'),
    url(r'^(?P<category_slug>[a-z0-9-_]+)/(?P<page_slug>[a-z0-9-_]+)/$', 'view_page', name='view_page'),
)