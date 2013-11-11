# -*- coding: utf-8 -*-
from django.conf.urls import url, patterns

from modeltranslation.settings import AVAILABLE_LANGUAGES

from .views import CategoryDetailView, PageDetailView

urlpatterns = list()


# Define all urls given available languages
for language_code in AVAILABLE_LANGUAGES:
    # All urls are prefixed by the language code for translated slugs
    # resolution
    base_url = r'^%s/' % language_code

    urlpatterns += patterns('',

        # Category
        url(base_url + r'(?P<slug_%s>[-\w]+)/$' % language_code,
            CategoryDetailView.as_view(),
            name='category_detail_%s' % language_code),

        # Page
        url(base_url + r'(?P<category_slug>[-\w]+)/(?P<slug_%s>[-\w]+)/$' % (
                language_code
            ),
            PageDetailView.as_view(),
            name='page_detail_%s' % language_code),
    )
