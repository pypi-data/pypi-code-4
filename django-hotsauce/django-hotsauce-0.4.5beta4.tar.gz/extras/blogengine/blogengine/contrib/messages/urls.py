#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2009-2011 Etienne Robillard <erob@gthcfoundation.org>
# All rights reserved.
# Please see the "LICENSE" file for license details. 

from notmm.utils.urlmap import RegexURLMap
from blogengine.utils import direct_to_template

urlpatterns = RegexURLMap()

urlpatterns.add_routes('blogengine.contrib.messages.views',
    (r'^messages/post/$', 'post'),    # post interface (ajax only)
    (r'^(?P<username>[\w]+)/messages/$', 'message_list'), # message list
    (r'^(?P<username>[\w]+)/messages/(?P<oid>[-\S]+)$', 'details') # message detail with hash
    )

