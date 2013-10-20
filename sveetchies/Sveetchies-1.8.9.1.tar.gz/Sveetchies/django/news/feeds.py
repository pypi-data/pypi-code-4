# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.syndication.views import Feed

from Sveetchies.django.pywiki2xhtml import PYWIKI2XHTML_CONFIGSET, PYWIKI2XHTML_DEFAULT_ACTIVED_MACROS
from Sveetchies.django.pywiki2xhtml.utils import configure_w2x_instance

from Sveetchies.django.news import NEWS_ENTRIES_PAGINATION
from Sveetchies.django.news.models import Category, Entry

safe_attachments_macros = list(PYWIKI2XHTML_DEFAULT_ACTIVED_MACROS)
safe_attachments_macros.remove('attach')

class LatestEntriesFeed(Feed):
    def get_object(self, request, category_slug):
        category_object = get_object_or_404(Category, slug=category_slug)
        self._w2x_object_description = configure_w2x_instance(request, actived_macros=safe_attachments_macros, configset_kwargs=PYWIKI2XHTML_CONFIGSET['short'])
        self._w2x_item_introduction = configure_w2x_instance(request, actived_macros=safe_attachments_macros, configset_kwargs=PYWIKI2XHTML_CONFIGSET['short'])
        self._w2x_item_content = configure_w2x_instance(request, actived_macros=safe_attachments_macros, configset_kwargs=PYWIKI2XHTML_CONFIGSET['standard'])
        return category_object
    
    def title(self, category_object):
        return u"Semper-Eadem.com - {0}".format(category_object.title)
    
    def link(self, category_object):
        return reverse('news-category-feed', args=[category_object.slug])
    
    def description(self, category_object):
        return self._w2x_object_description.transform(category_object.description)
    
    def items(self, category_object):
        return Entry.objects.filter(category=category_object).order_by('-publish_date')[:10]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        if item.introduction:
            return self._w2x_item_introduction.transform(item.introduction)
        return self._w2x_item_content.transform(item.content)
