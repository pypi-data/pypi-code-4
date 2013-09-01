"""
Created on Nov 6, 2012

@author: Nicklas Boerjesson
@note: This decorator raises an error if a certain method is decorated
"""
from decorator import decorator
# from .aspect_utilities import alter_function_parameter_and_call

def _not_implemented(func, *args, **kwargs):
    raise Exception('Internal error in "' + func.__name__ +'": Not implemented.')


def not_implemented(f):
    """Raises an "Internal error in func: Not implemented."""
    return decorator(_not_implemented, f)
