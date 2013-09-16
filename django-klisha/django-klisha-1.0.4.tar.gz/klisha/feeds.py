# coding=utf-8
#
# Copyright (c) 2008-2013 by zenzire - http://www.zenzire.com
# Author Marcin Mierzejewski
#

from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from .settings import KLISHA_WEBSITE_NAME
from .models import Picture


class PicturesFeed(Feed):
    title = KLISHA_WEBSITE_NAME
    description_template = "feeds/picture_description.html"
    link = "/rss/" 

    def items(self):
        return Picture.published_objects.order_by('-published_at')[:20]

    def item_title(self, item):
        return item.title

    def item_link(self, item):
        return reverse('picture-detail', args=[item.slug])
    
    def item_description(self, item):
        if item.description:
            desc = item.description
        else:
            desc = ""
        return desc

feeds = {'picture': PicturesFeed}
