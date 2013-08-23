"""This is the generic function package."""


from base import generic, method, variadic_method
from go import *

__all__ = go.__all__[:]
__all__.extend(("generic", "method", "variadic_method"))
