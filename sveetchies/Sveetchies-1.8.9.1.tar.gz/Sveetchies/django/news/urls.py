# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from Sveetchies.django.news.models import Category, Entry
from Sveetchies.django.news.feeds import LatestEntriesFeed

# Configs pour les vues de preview
basic_short_preview = {'default_configset_name': 'short'}
category_object_preview_kwargs = {
    'model_object': Category,
    'default_configset_name': 'short'
}
entry_object_preview_introduction_kwargs = {
    'model_object': Entry,
    'default_configset_name': 'short',
}
entry_object_preview_content_kwargs = {
    'model_object': Entry,
}

urlpatterns = patterns('',
    url(r'^category/(?P<category_slug>[-\w]+)/$', 'Sveetchies.django.news.views.category_details_by_slug', name="news-category-details"),
    url(r'^category/(?P<category_slug>[-\w]+)/rss/$', LatestEntriesFeed(), name="news-category-feed"),

    url(r'^category/(?P<category_slug>[-\w]+)/(?P<entry_slug>[-\w]+)/$', 'Sveetchies.django.news.views.entry_details_by_slug', name="news-entry-details"),
    
    url(r'^admin/category/preview/$', 'Sveetchies.django.pywiki2xhtml.views.preview', kwargs=basic_short_preview, name="news-admin-category-preview"),
    url(r'^admin/category/(?P<instance_id>\d+)/preview/$', 'Sveetchies.django.pywiki2xhtml.views.model_object_preview', kwargs=category_object_preview_kwargs, name="news-admin-category-object-preview"),

    url(r'^admin/entry/introduction/preview/$', 'Sveetchies.django.pywiki2xhtml.views.preview', kwargs=basic_short_preview, name="news-admin-entry-introduction-preview"),
    url(r'^admin/entry/(?P<instance_id>\d+)/introduction/preview/$', 'Sveetchies.django.pywiki2xhtml.views.model_object_preview', kwargs=entry_object_preview_introduction_kwargs, name="news-admin-entry-object-introduction-preview"),
    
    url(r'^admin/entry/content/preview/$', 'Sveetchies.django.pywiki2xhtml.views.preview', kwargs={}, name="news-admin-entry-content-preview"),
    url(r'^admin/entry/(?P<instance_id>\d+)/content/preview/$', 'Sveetchies.django.pywiki2xhtml.views.model_object_preview', kwargs=entry_object_preview_content_kwargs, name="news-admin-entry-object-content-preview"),
    
    url(r'^syntax/$', 'Sveetchies.django.pywiki2xhtml.views.syntax_help_staff_member_required', name="news-syntax_help"),
)
