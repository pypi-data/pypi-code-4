#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2007-2012 Etienne Robillard <erob@gthcfoundation.org>
# All rights reserved.
# Please see the "LICENSE" file for license details. 
"""Details views"""

from urlparse import parse_qsl
from datetime import datetime
from operator import attrgetter
from django.template import RequestContext

from blogengine.config          import ObjectDoesNotExist
from blogengine.contrib.api_v1  import CategoryManager
from blogengine.contrib.comments import CommentForm
from blogengine.template        import direct_to_template

from notmm.dbapi.orm.decorators import with_schevo_database
from notmm.utils.django_settings import LazySettings

settings = LazySettings()

@with_schevo_database(settings.SCHEVO['DATABASE_NAME'])
def users(request, *args, **kwargs):
    """View the list of registered users with a link to their public
    profile page"""
    db = request.environ['schevo.db.blogs']
    Q = db.Q
    ## Get the most recent entries in reverse order
    #q1 = Q.Match(db.BlogEntry, 'pub_date', '<=', datetime.today())
    #q2 = Q.Match(db.BlogEntry, 'reviewed', '==', True)
    #q3 = Q.Match(db.BlogEntry, 'author', '==', request.session.user)

    # selects elements contained in both sets
    #results = Q.Intersection(q1, q2)
    
    return direct_to_template(request, \
        template_name='blogengine/listview_users.mako', 
        extra_context=RequestContextWrapper(request, dict(
            )),
        #extra_headers=extra_headers,
        #cache_enabled=False
        )

