#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2007-2011 Etienne Robillard <erob@gthcfoundation.org>
# All rights reserved.
# 
# TODO: This module needs heavy refactoring.. ;-)

"""Decorators functions returning a callable"""

from functools import wraps
from session import ScopedSession as scoped_session

__all__ = ('with_session',)

def with_session(engine=None):
    """
    Decorator function for attaching a `` Session`` instance
    as a keyword argument in ``request.environ``. 
    """
    def decorator(view_func):
        def _wrapper(request, *args, **kwargs):
            if engine is not None:
                Session = scoped_session()
                Session.set_session(engine)
                request.environ['_scoped_session'] = getattr(scoped_session, 'session')
            return view_func(request, *args, **kwargs)
        return wraps(view_func)(_wrapper)
    return decorator

