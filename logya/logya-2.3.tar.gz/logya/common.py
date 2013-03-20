# -*- coding: utf-8 -*-
import warnings
import functools


def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used.

    Code from
    http://wiki.python.org/moin/PythonDecoratorLibrary#Generating_Deprecation_Warnings
    """

    @functools.wraps(func)
    def new_func(*args, **kwargs):
        warnings.warn_explicit(
            "Call to deprecated function %(funcname)s." % {
                'funcname': func.__name__,
            },
            category=DeprecationWarning,
            filename=func.func_code.co_filename,
            lineno=func.func_code.co_firstlineno + 1
        )
        return func(*args, **kwargs)
    return new_func
