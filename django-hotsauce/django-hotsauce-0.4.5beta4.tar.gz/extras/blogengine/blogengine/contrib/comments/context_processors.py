#!/usr/bin/env python
# -*- coding: utf-8 -*-

from forms import CommentForm

__all__ = ['comment_form']


def comment_form(request):
    """Simple comment form processor"""
    return {'comment_form' : CommentForm()}

#def get_comment_list(request):
#    """Get a set of comments for the current request object"""
#    ctx['comment_list'] = CommentManager.objects.filter(path_url=request.environ['PATH_INFO'])
