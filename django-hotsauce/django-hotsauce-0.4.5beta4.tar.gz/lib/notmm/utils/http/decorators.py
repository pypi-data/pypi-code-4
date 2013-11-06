#!/usr/bin/env python
"""Common decorators for integration in generic views."""

from functools import wraps
from notmm.utils.wsgilib import HTTPForbiddenResponse

def post_required(view_func, **kwargs):
    def _wrapper(*args, **kwargs):
        req = args[0]
        if (req.method != 'POST'):
            return HTTPForbiddenResponse("Please use POST!", status=403, mimetype='text/plain')
        return view_func(req, *args, **kwargs)
    return wraps(view_func)(_wrapper, **kwargs)
