# -*- coding: utf-8 -*-
from datetime import datetime
from django.contrib.syndication.views import Feed
from sh.app.news.models import NewsItem

class NewsRssFeed(Feed):
    title = "Starthjelpa"
    link = "/news/"
#    description = ""

    def items(self):
        return NewsItem.objects.filter(pub_date__lte=datetime.now)[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.content