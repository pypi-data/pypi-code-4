#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 Etienne Robillard <erob@gthcfoundation.org>
# All rights reserved.
# Please see the "LICENSE" file for license details. 
"""Details views"""

from blogengine.contrib.blog.views import *
from blogengine.handlers import handle404

#@authorize(RemoteUser())
@with_schevo_database(DATABASE_NAME)
def details_for_category(request, **kwargs):
    """Shows the details for a Category entity (instance of)"""
    
    #print 'in details_for_category', kwargs
    db = request.environ['schevo.db.'+DATABASE_NAME]

    # get the extent class if defined
    template_name = kwargs.pop('template_name', 
        'blogengine/browse_by_category.mako')
    # Try to lookup a category first
    related = []
    try:
        #obj = get_entity_by_string(('slug', slug), db, extent='Category')
        obj = db.Category.findone(slug=kwargs['slug'])
    except ObjectDoesNotExist:
        raise ObjectDoesNotExist('no such category: %s' % kwargs['slug'])
    else:
        if obj is not None:
            related = obj.x.blogentries() 

    return direct_to_template(request, template_name, 
        extra_context=RequestContext(request, 
            {'instance': obj, 'related_items' : related}))

#@authorize(RemoteUser())
# should go in detail.py
@with_schevo_database(DATABASE_NAME)
def details_for_blogentry(request, **kwargs):
    """Shows the details for a BlogEntry entity (instance of)"""
    
    db = request.db

    if 'extra_context' in kwargs:
        params = kwargs['extra_context'].copy()
    else:
        params = {'comment_form' : CommentForm()}

    template_name = kwargs.pop('template_name', 'blogengine/blogentry_detail.mako')
    
    try:
       result = db.BlogEntry.findone(slug=kwargs['slug'])
    except ObjectDoesNotExist:

        return handle404(request, referer=True, instance=log)
    else:
        if result is not None:
            params['result'] = result
            params['path'] = result.get_absolute_url()
            # fetch the related comments for this post
            comments = result.x.comments()
            unpublished_comments = [item for item in comments if not item.x.is_published()]
            published_comments = set(comments).difference(unpublished_comments)
            # List of published (visible) comments
            params['comments'] = list(published_comments)
            # List of unpublished comments 
            params['u_comments_count'] = len(unpublished_comments)

    #db.close()
    
    return direct_to_template(request, template_name, extra_context=params)
        
