#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (c) 2007-2012 Etienne Robillard <erob@gthcfoundation.org>
# All rights reserved.
#
# Please see the "LICENSE" file for license details. 

from notmm.utils.urlmap import RegexURLMap, url

urlpatterns = RegexURLMap()
urlpatterns.add_routes('blogengine.contrib.comments.views',
    # Add comment form
    #(r'^(?P<category>[-\w]+)/(?P<slug>[-\w]+)/comment/$', 'preview_comment'),
    # Save new comment -> JSON encoded response
    url(r'^new/$', 'save_comment')
)
