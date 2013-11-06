#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2007-2012 Etienne Robillard 
# All rights reserved.
# Please see the "LICENSE" file for license details. 
"""Views for allowing people to post comments."""

import demjson

from datetime import datetime
from notmm.utils.http import post_required
from notmm.utils.wsgilib import HTTPResponse, HTTPRedirectResponse
from notmm.dbapi.orm import decorators
from notmm.utils.django_settings import LazySettings

settings = LazySettings()

#from blogengine.utils import get_entity_by_string, get_extent_class
from blogengine.template import direct_to_template
from blogengine.config import RemoteUser, authorize
from blogengine.contrib.api_v1.model import BlogEntryManager
from forms import CommentForm

default_manager = BlogEntryManager()

#import logging
#logger = logging.Logger('blogengine')
#logger.setLevel(logging.DEBUG)

def _get_raw_errors(form):
    return dict([(name, u"%s" % error[0]) for name, error in form.errors.iteritems() ])

@post_required
@decorators.with_schevo_database(settings.SCHEVO['DATABASE_NAME'])
def preview_comment(request, *args, **kwargs):

    path_url = request.POST.pop('id_path')
    # blogentry.oid
    

    oid = request.POST.pop('id_oid')

    form = CommentForm(request.POST.copy())
    status = 200
    if form.is_valid():
        # If the form is cleaned from hazardous input, let the user
        # confirm its validity with a form preview then create
        # the entity in the db.
        db = request.db # pointer to the correct db...
        #print "pointer pointer baby!"
        save_comment(oid, path_url, db, form.cleaned_data)
        # comment saved, redirect to the blog url
        #return HTTPRedirectResponse(path_url)
        json = demjson.encode(dict(result="comment saved!"))
    else:
        # Form needs to be corrected, return it back
        # print 'form contains errors!'
        raw_errors = _get_raw_errors(form)
        # Translate form errors into a JSON object
        json = demjson.encode(dict(errors=raw_errors))
        status = 400 # Bad request
    return HTTPResponse(str(json), mimetype='application/javascript', status=status)

def save_comment(oid, path, db, new_data):
    """Save a comment for review/publishing by an admin"""

    if not 'subscribe_comment_thread' in new_data:
        # By default do not subscribe users unless explicitely
        # requested by the comment author
        new_data['subscribe_comment_thread'] = False
    
    # Path to the blog entry/url
    new_data['path_url'] = path

    # Entry oid
    new_data['blogentry'] = default_manager.objects.get_by_oid(oid)

    
    # Date the comment was posted
    new_data['pub_date'] = datetime.now()
    
    try:
        #TODO: use CommentManager class here to save comments
        tx = db.Comment.t.create(**new_data)
        if tx: 
            # TODO: save a log record in $error_log
            # logger = request.environ['logger']
            # logger.info('new comment saved')
            db.execute(tx)
            db.commit()
    except:
        #logger.debug('fatal error saving comment: %r' % e)
        raise
    return None    

