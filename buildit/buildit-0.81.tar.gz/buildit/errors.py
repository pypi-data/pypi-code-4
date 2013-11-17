'''
    Buildit - (C) 2011-2013, Mike Miller
    A simple build tool for small projects.  License: GPL3+
'''

# Exceptions
class BuildItError(RuntimeError): pass

# config errors
class AttrMissing(BuildItError): pass
class CircularReference(BuildItError): pass
class DepDoesNotExist(BuildItError): pass
class ReservedError(BuildItError): pass
class TargetDoesNotExist(BuildItError): pass

# execution errors
class ExecError(OSError): pass

