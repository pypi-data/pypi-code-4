#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2009 Etienne Robillard <erob@gthcfoundation.org>
# All rights reserved.
# Please see the "LICENSE" file for license details. 

from notmm.utils.urlmap import RegexURLMap, url
from notmm.utils.wsgilib import HTTPResponse, HTTPRedirectResponse

from blogengine.template import direct_to_template
from blogengine.contrib.api_v1.model import (
    CommentManager, BlogEntryManager, CategoryManager
    )




urlpatterns = RegexURLMap()

# Site-wide API functions accessible to registered users (editors, etc.)
urlpatterns.add_routes('blogengine.contrib.api_v1.actions',
    #(r'^posts/add/$', 'add'),
    url(r'^(?P<category>[-\w]+)/(?P<slug>[-\w]+)/edit/$', 'edit'),
    url(r'^(?P<category>[-\w]+)/(?P<slug>[-\w]+)/send_to_friend/$', 'send_to_friend'),
    url(r'^(?P<category>[-\w]+)/(?P<slug>[-\w]+)/delete/$', 'delete'),
    url(r'^create/$', 'add'),
   
  )

# Extended views   
urlpatterns.add_routes('blogengine.contrib.blog.views.detail',
    # list of all categories
    url(r'^categories/$', direct_to_template, 
        {'template_name': 'blogengine/categories.mako',
         'extra_context': {
            'categories': CategoryManager.objects.all()}
        }),
    # Browse by category view 
    url(r'^categories/(?P<slug>[-\w]+)/$', 'details_for_category', {
        'extent_class' : 'Category'
        }
    ),

    # Browse by category and slug, but attempt to match the slug
    # to a Category name first, to allow browsing by subcategory names.
    # Matching order:
    # 1. Category/Slug (investigations/the-sky-is-pink)
    # 2. Slug (the-sky-is-pink)
    # 3. Username (erob)
    url(r'^(?P<category>[-\w]+)/(?P<slug>[-\w]+)/$', 'details_for_blogentry')
    )

# Comments
urlpatterns.add_routes('blogengine.contrib.comments.views',
    url(r'^(?P<category>[-\w]+)/(?P<slug>[-\w]+)/comment/new/$', 'preview_comment'),
    url(r'^(?P<category>[-\w]+)/(?P<slug>[-\w]+)/comment/done/$', 'save_comment')
    )

urlpatterns.include('blogengine.contrib.blog.urls')

# urlpatterns.include(admin.site.urls)
