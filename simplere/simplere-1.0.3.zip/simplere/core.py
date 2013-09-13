"""
A simpler way to access and use regular expressions. As a bonus,
also simpler access to globs.
"""

from mementos import MementoMetaclass, with_metaclass
import sys
import re
import fnmatch

_PY3 = sys.version_info[0] == 3
if _PY3:
    basestring = str


class ReMatch(object):

    """
    An easier-to-use proxy for regular expression match objects. Ideally this
    would be a subclass of the re module's match object, but their type
    ``_sre.SRE_Match`` appears to be unsubclassable
    <http://stackoverflow.com/questions/4835352/subclassing-matchobject-in-python>`_.
    Thus, ReMatch is a proxy exposes the match object's numeric (positional) and
    named groups through indices and attributes. If a named group has the same
    name as a match object method or property, it takes precedence. Either
    change the name of the match group or access the underlying property thus:
    ``x._match.property``
    """

    def __init__(self, match=None):
        self._match = match
        self._groupdict = None

    def _bool(self):
        """
        Return True if the match was successful, and False if it failed.
        """
        return bool(self._match)

    if _PY3:
        __bool__ = _bool
    else:
        __nonzero__ = _bool

    def __getattr__(self, name):
        if self._match is None:
            raise AttributeError(
                "Empty match has no such attribute '{}'".format(name))

        if self._groupdict is None:
            self._groupdict = self._match.groupdict()

        if name in self.__dict__:
            return self.__dict__[name]
        if name in self._groupdict:
            return self._groupdict[name]
        try:
            return getattr(self._match, name)
        except AttributeError:
            raise AttributeError("no such attribute '{}'".format(name))

    def __getitem__(self, index):
        return self._match.group(index)

    def __div__(self, other):
        """
        Define the div (/) operation for en passant usage.
        """
        self._match = other._match if isinstance(other, ReMatch) else other
        self._groupdict = None
        return other
        
    if _PY3:
        __truediv__ = __div__
        
    __lt__ = __div__
    __le__ = __div__

    
Match = ReMatch     # define alias
match = Match()     # instantiate global match instance

function_type = type(lambda: True)   # define our own because not def'd in py26

def is_function(obj):
    """
    Determines: Is obj a function?
    """
    return isinstance(obj, function_type)

def regrouped(f):
    """
    Takes a function f that is supposed to get _sre.SRE_Match objects and
    wraps each of those with a ReMatch proxy. If not a function (ie, probably
    a string, then just return it.)
    """
    if not hasattr(f, '__call__'):
        return f
    
    def regrouped_fn(match):
        return f(ReMatch(match))
    
    return regrouped_fn

class Re(with_metaclass(MementoMetaclass, object)):

    # convenience copy of re flag constants
    
    DEBUG      = re.DEBUG
    I          = re.I
    IGNORECASE = re.IGNORECASE
    L          = re.L
    LOCALE     = re.LOCALE
    M          = re.M
    MULTILINE  = re.MULTILINE
    S          = re.S
    DOTALL     = re.DOTALL
    U          = re.U
    UNICODE    = re.UNICODE
    X          = re.X
    VERBOSE    = re.VERBOSE
    
    _ = None

    def __init__(self, pattern, flags=0):
        self.pattern    = pattern
        self.flags      = flags
        self.re = pattern if type(pattern).__name__ == 'SRE_Pattern' else re.compile(pattern, flags)
        self.groups     = self.re.groups
        self.groupindex = self.re.groupindex
        
        # can't use isinstance() test on pattern because _sre objects are damn hard to
        # import or wrangle. Name test is best I know how to do.
        
    def _regroup(self, m):
        """
        Given an _sre.SRE_Match object, create and return a corresponding
        ReMatch object.
        """
        result = ReMatch(m) if m else m
        Re._ = result
        return result

    def __contains__(self, item):
        if not isinstance(item, basestring):
             item = str(item)
        return self._regroup(self.re.search(item))
    
    ### methods that return ReMatch objects
    
    def search(self, *args, **kwargs):
        return self._regroup(self.re.search(*args, **kwargs))

    def match(self, *args, **kwargs):
        return self._regroup(self.re.match(*args, **kwargs))
    
    def finditer(self, *args, **kwargs):
        for m in self.re.finditer(*args, **kwargs):
            yield self._regroup(m)
    
    ### methods that don't need ReMatch objects
      
    def findall(self, *args, **kwargs):
        return self.re.findall(*args, **kwargs)
    
    def split(self, *args, **kwargs):
        return self.re.split(*args, **kwargs)
    
    def sub(self, repl, string, *args, **kwargs):
        return self.re.sub(regrouped(repl), string, *args, **kwargs)
    
    def subn(self, repl, *args, **kwargs):
        return self.re.subn(regrouped(repl), string, *args, **kwargs)
    
    def escape(self, *args, **kwargs):
        return self.re.escape(*args, **kwargs)        
  

class Glob(with_metaclass(MementoMetaclass, object)):
    """
    An item matches a Glob via Unix filesystem glob semantics.
    
    E.g. 'alpha' matches 'a*' and 'a????' but not 'b*'
    """

    def __init__(self, pattern):
        self.pattern = pattern
        
    def __contains__(self, item):
        return fnmatch.fnmatch(str(item), self.pattern)
