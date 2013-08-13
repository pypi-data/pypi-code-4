# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.utils.translation import ugettext_lazy as _
from sh.app.news.feeds import NewsRssFeed

urlpatterns = patterns('sh.app.news.views',
    url(r'^$', 'news_feed', name='news'),
    url(_(r'^feed/$'), NewsRssFeed()),
    url(_(r'^add/$'), 'edit_item', name='add_item'),
    url(_(r'^(?P<id>\d+)/edit/$'), 'edit_item', name='edit_item'),
    url(_(r'^(?P<item_slug>[a-z0-9-_]+)/$'), 'view_item', name='view_item'),
)
