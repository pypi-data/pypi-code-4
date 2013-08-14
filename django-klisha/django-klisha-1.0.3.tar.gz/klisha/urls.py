# coding=utf-8
#
# Copyright (c) 2008-2013 by zenzire - http://www.zenzire.com
# Author Marcin Mierzejewski
#

from django.conf.urls import patterns, url
from . import views
from .feeds import PicturesFeed

urlpatterns = patterns('',
    url('^$', views.picture_list, name='picture-list'),
    url('^tags/$', views.tag_list, name='tag-list'),
    url('^tags/(?P<slug>[0-9A-Za-z-]+)/$', views.tag_detail, name='tag-detail'),
    url('^categories/$', views.category_list, name='category-list'),
    url('^categories/(?P<slug>[0-9A-Za-z-]+)/$', views.category_detail, name='category-detail'),
    url(r'^archive/', views.archive_list, name='archive-list'),
    url(r'^popular/$', views.popular_list, name='popular-list'), 
    url(r'^rss/$', PicturesFeed()),
    url(r'^(?P<year>\d{4})/$', views.picture_list, name='picture-list-year'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/$', views.picture_list, name='picture-list-year-month'),
    url(r'^(?P<slug>[0-9A-Za-z-]+)/$', views.picture_detail, name="picture-detail"),    
)
