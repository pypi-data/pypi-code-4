"""
Definition of common exceptions
"""

from say import FmtException

class ArgsUnavailable(FmtException, ValueError):
    pass

class BadValue(FmtException, ValueError):
    pass

class ParseError(FmtException, RuntimeError):
    pass