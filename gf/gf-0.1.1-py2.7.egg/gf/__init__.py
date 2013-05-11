"""This is the generic function package."""


from base import generic, method
from go import *

__all__ = go.__all__[:]
__all__.extend(("generic", "method"))
