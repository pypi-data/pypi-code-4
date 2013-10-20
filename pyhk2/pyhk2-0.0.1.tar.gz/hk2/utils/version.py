# from distutils module

import string, re
from types import StringType

class Version:
    """ A version number consists of two or three dot-separated numeric 
    components, with an optional "pre-release" tag on the end.  
    The pre-release tag consists of the letter 'a' or 'b' followed 
    by a number.  If the numeric components of two version numbers 
    are equal, then one with a pre-release tag will always
    be deemed earlier (lesser) than one without.
    
    The following are valid version numbers (shown in the order that
    would be obtained by sorting according to the supplied cmp function):
    
        0.4       0.4.0  (these two are equivalent)
        0.4.1
        0.5a1
        0.5b3
        0.5
        0.9.6
        1.0
        1.0.4a3
        1.0.4b1
        1.0.4
    
    The following are examples of invalid version numbers:
    
        1
        2.7.2.2
        1.3.a4
        1.3pl1
        1.3c4
    """

    version_re = re.compile(r'^(\d+) \. (\d+) (\. (\d+))? ([ab](\d+))?$',
                            re.VERBOSE)
    
    def __init__ (self, vstring=None):
        if vstring:
            self.parse(vstring)
        else:
            self.prerelease = None
            self.version = (0, 0, 0)
    
    def __repr__ (self):
        return "%s ('%s')" % (self.__class__.__name__, str(self))
    
    def parse (self, vstring):
        match = self.version_re.match(vstring)
        if not match:
            raise ValueError, "invalid version number '%s'" % vstring
        
        (major, minor, patch, prerelease, prerelease_num) = \
            match.group(1, 2, 4, 5, 6)
        
        if patch:
            self.version = tuple(map(string.atoi, [major, minor, patch]))
        else:
            self.version = tuple(map(string.atoi, [major, minor]) + [0])
        
        if prerelease:
            self.prerelease = (prerelease[0], string.atoi(prerelease_num))
        else:
            self.prerelease = None
    
    
    def __str__ (self):
        
        if self.version[2] == 0:
            vstring = string.join(map(str, self.version[0:2]), '.')
        else:
            vstring = string.join(map(str, self.version), '.')
        
        if self.prerelease:
            vstring = vstring + self.prerelease[0] + str(self.prerelease[1])
        
        return vstring
    
    
    def __cmp__ (self, other):
        if isinstance(other, StringType):
            other = Version(other)
        
        compare = cmp(self.version, other.version)
        if (compare == 0):              # have to compare prerelease
            
            # case 1: neither has prerelease; they're equal
            # case 2: self has prerelease, other doesn't; other is greater
            # case 3: self doesn't have prerelease, other does: self is greater
            # case 4: both have prerelease: must compare them!
            
            if (not self.prerelease and not other.prerelease):
                return 0
            elif (self.prerelease and not other.prerelease):
                return -1
            elif (not self.prerelease and other.prerelease):
                return 1
            elif (self.prerelease and other.prerelease):
                return cmp(self.prerelease, other.prerelease)
            
        else:                           # numeric versions don't match --
            return compare              # prerelease stuff doesn't matter
