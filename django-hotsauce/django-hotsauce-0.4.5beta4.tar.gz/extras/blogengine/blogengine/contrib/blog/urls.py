#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2009-2011 Etienne Robillard <EMAIL=ORG1>
# All rights reserved.
# <LICENSE=ISC>

from notmm.utils.urlmap import RegexURLMap, url

from blogengine.template import direct_to_template
from blogengine.contrib.api_v1.model import CommentManager, BlogEntryManager, CategoryManager

urlpatterns = RegexURLMap() # w00t! w00t! :)

urlpatterns.add_routes('blogengine.contrib.blog.views.detail', 
# browse by category view 
    url(r'categories/(?P<slug>[-\w]+)/$', 'details_for_category', {
        'extent_class' : 'Category'})
        )

urlpatterns.add_routes('',
# list of all categories
    url(r'categories/$', direct_to_template, 
        {'template_name': 'blogengine/categories.mako',
         'extra_context': {
            'categories'   : CategoryManager.objects.all()}
        }
    ),
)
urlpatterns.add_routes('blogengine.contrib.blog.views.index',
    # XXX archive view 
    url(r'^$', 'index'),
    # Add/edit a new Entry ("BlogEntry") 
    # smart version: will handle proper authorization and allow
    # making updates. (login required)
    #url(r'posts/add/$', 'add'),    
)


