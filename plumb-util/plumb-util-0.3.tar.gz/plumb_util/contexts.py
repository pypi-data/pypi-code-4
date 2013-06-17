"""
Routines for working with variably-nested contexts
"""
from functools import wraps

def wrap_with_context_thunk(thunk, func):
    """
    Wrap func with a context manager returned by thunk
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        with thunk():
            return func(*args, **kwargs)

    return wrapper

def wrap_with_contexts(context_thunks, func):
    """
    Wrap func with zero or more nested context managers returned by thunks in
    context_thunks. The outermost context manager is taken from the first thunk.
    """
    # Wrap the function
    wrapper = func
    for thunk in reversed(context_thunks):
        wrapper = wrap_with_context_thunk(thunk, wrapper)
    return wrapper
