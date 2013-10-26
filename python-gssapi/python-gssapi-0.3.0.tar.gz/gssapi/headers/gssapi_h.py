'''Wrapper for gssapi.h

Generated with:
/Users/hugh/Source/python-gssapi/venv/bin/ctypesgen.py --cpp gcc -E -DTARGET_CPU_X86_64 -D__attribute__\(x\)= -framework GSS -lGSS -i uid_t -o build/lib/gssapi/headers/gssapi_h.py /System/Library/Frameworks/GSS.framework/Headers/gssapi.h /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h

Do not modify this file.
'''

__docformat__ =  'restructuredtext'

# Begin preamble

import ctypes, os, sys
from ctypes import *

_int_types = (c_int16, c_int32)
if hasattr(ctypes, 'c_int64'):
    # Some builds of ctypes apparently do not have c_int64
    # defined; it's a pretty good bet that these builds do not
    # have 64-bit pointers.
    _int_types += (c_int64,)
for t in _int_types:
    if sizeof(t) == sizeof(c_size_t):
        c_ptrdiff_t = t
del t
del _int_types

class c_void(Structure):
    # c_void_p is a buggy return type, converting to int, so
    # POINTER(None) == c_void_p is actually written as
    # POINTER(c_void), so it can be treated as a real pointer.
    _fields_ = [('dummy', c_int)]

def POINTER(obj):
    p = ctypes.POINTER(obj)

    # Convert None to a real NULL pointer to work around bugs
    # in how ctypes handles None on 64-bit platforms
    if not isinstance(p.from_param, classmethod):
        def from_param(cls, x):
            if x is None:
                return cls()
            else:
                return x
        p.from_param = classmethod(from_param)

    return p

class UserString:
    def __init__(self, seq):
        if isinstance(seq, basestring):
            self.data = seq
        elif isinstance(seq, UserString):
            self.data = seq.data[:]
        else:
            self.data = str(seq)
    def __str__(self): return str(self.data)
    def __repr__(self): return repr(self.data)
    def __int__(self): return int(self.data)
    def __long__(self): return long(self.data)
    def __float__(self): return float(self.data)
    def __complex__(self): return complex(self.data)
    def __hash__(self): return hash(self.data)

    def __cmp__(self, string):
        if isinstance(string, UserString):
            return cmp(self.data, string.data)
        else:
            return cmp(self.data, string)
    def __contains__(self, char):
        return char in self.data

    def __len__(self): return len(self.data)
    def __getitem__(self, index): return self.__class__(self.data[index])
    def __getslice__(self, start, end):
        start = max(start, 0); end = max(end, 0)
        return self.__class__(self.data[start:end])

    def __add__(self, other):
        if isinstance(other, UserString):
            return self.__class__(self.data + other.data)
        elif isinstance(other, basestring):
            return self.__class__(self.data + other)
        else:
            return self.__class__(self.data + str(other))
    def __radd__(self, other):
        if isinstance(other, basestring):
            return self.__class__(other + self.data)
        else:
            return self.__class__(str(other) + self.data)
    def __mul__(self, n):
        return self.__class__(self.data*n)
    __rmul__ = __mul__
    def __mod__(self, args):
        return self.__class__(self.data % args)

    # the following methods are defined in alphabetical order:
    def capitalize(self): return self.__class__(self.data.capitalize())
    def center(self, width, *args):
        return self.__class__(self.data.center(width, *args))
    def count(self, sub, start=0, end=sys.maxint):
        return self.data.count(sub, start, end)
    def decode(self, encoding=None, errors=None): # XXX improve this?
        if encoding:
            if errors:
                return self.__class__(self.data.decode(encoding, errors))
            else:
                return self.__class__(self.data.decode(encoding))
        else:
            return self.__class__(self.data.decode())
    def encode(self, encoding=None, errors=None): # XXX improve this?
        if encoding:
            if errors:
                return self.__class__(self.data.encode(encoding, errors))
            else:
                return self.__class__(self.data.encode(encoding))
        else:
            return self.__class__(self.data.encode())
    def endswith(self, suffix, start=0, end=sys.maxint):
        return self.data.endswith(suffix, start, end)
    def expandtabs(self, tabsize=8):
        return self.__class__(self.data.expandtabs(tabsize))
    def find(self, sub, start=0, end=sys.maxint):
        return self.data.find(sub, start, end)
    def index(self, sub, start=0, end=sys.maxint):
        return self.data.index(sub, start, end)
    def isalpha(self): return self.data.isalpha()
    def isalnum(self): return self.data.isalnum()
    def isdecimal(self): return self.data.isdecimal()
    def isdigit(self): return self.data.isdigit()
    def islower(self): return self.data.islower()
    def isnumeric(self): return self.data.isnumeric()
    def isspace(self): return self.data.isspace()
    def istitle(self): return self.data.istitle()
    def isupper(self): return self.data.isupper()
    def join(self, seq): return self.data.join(seq)
    def ljust(self, width, *args):
        return self.__class__(self.data.ljust(width, *args))
    def lower(self): return self.__class__(self.data.lower())
    def lstrip(self, chars=None): return self.__class__(self.data.lstrip(chars))
    def partition(self, sep):
        return self.data.partition(sep)
    def replace(self, old, new, maxsplit=-1):
        return self.__class__(self.data.replace(old, new, maxsplit))
    def rfind(self, sub, start=0, end=sys.maxint):
        return self.data.rfind(sub, start, end)
    def rindex(self, sub, start=0, end=sys.maxint):
        return self.data.rindex(sub, start, end)
    def rjust(self, width, *args):
        return self.__class__(self.data.rjust(width, *args))
    def rpartition(self, sep):
        return self.data.rpartition(sep)
    def rstrip(self, chars=None): return self.__class__(self.data.rstrip(chars))
    def split(self, sep=None, maxsplit=-1):
        return self.data.split(sep, maxsplit)
    def rsplit(self, sep=None, maxsplit=-1):
        return self.data.rsplit(sep, maxsplit)
    def splitlines(self, keepends=0): return self.data.splitlines(keepends)
    def startswith(self, prefix, start=0, end=sys.maxint):
        return self.data.startswith(prefix, start, end)
    def strip(self, chars=None): return self.__class__(self.data.strip(chars))
    def swapcase(self): return self.__class__(self.data.swapcase())
    def title(self): return self.__class__(self.data.title())
    def translate(self, *args):
        return self.__class__(self.data.translate(*args))
    def upper(self): return self.__class__(self.data.upper())
    def zfill(self, width): return self.__class__(self.data.zfill(width))

class MutableString(UserString):
    """mutable string objects

    Python strings are immutable objects.  This has the advantage, that
    strings may be used as dictionary keys.  If this property isn't needed
    and you insist on changing string values in place instead, you may cheat
    and use MutableString.

    But the purpose of this class is an educational one: to prevent
    people from inventing their own mutable string class derived
    from UserString and than forget thereby to remove (override) the
    __hash__ method inherited from UserString.  This would lead to
    errors that would be very hard to track down.

    A faster and better solution is to rewrite your program using lists."""
    def __init__(self, string=""):
        self.data = string
    def __hash__(self):
        raise TypeError("unhashable type (it is mutable)")
    def __setitem__(self, index, sub):
        if index < 0:
            index += len(self.data)
        if index < 0 or index >= len(self.data): raise IndexError
        self.data = self.data[:index] + sub + self.data[index+1:]
    def __delitem__(self, index):
        if index < 0:
            index += len(self.data)
        if index < 0 or index >= len(self.data): raise IndexError
        self.data = self.data[:index] + self.data[index+1:]
    def __setslice__(self, start, end, sub):
        start = max(start, 0); end = max(end, 0)
        if isinstance(sub, UserString):
            self.data = self.data[:start]+sub.data+self.data[end:]
        elif isinstance(sub, basestring):
            self.data = self.data[:start]+sub+self.data[end:]
        else:
            self.data =  self.data[:start]+str(sub)+self.data[end:]
    def __delslice__(self, start, end):
        start = max(start, 0); end = max(end, 0)
        self.data = self.data[:start] + self.data[end:]
    def immutable(self):
        return UserString(self.data)
    def __iadd__(self, other):
        if isinstance(other, UserString):
            self.data += other.data
        elif isinstance(other, basestring):
            self.data += other
        else:
            self.data += str(other)
        return self
    def __imul__(self, n):
        self.data *= n
        return self

class String(MutableString, Union):

    _fields_ = [('raw', POINTER(c_char)),
                ('data', c_char_p)]

    def __init__(self, obj=""):
        if isinstance(obj, (str, unicode, UserString)):
            self.data = str(obj)
        else:
            self.raw = obj

    def __len__(self):
        return self.data and len(self.data) or 0

    def from_param(cls, obj):
        # Convert None or 0
        if obj is None or obj == 0:
            return cls(POINTER(c_char)())

        # Convert from String
        elif isinstance(obj, String):
            return obj

        # Convert from str
        elif isinstance(obj, str):
            return cls(obj)

        # Convert from c_char_p
        elif isinstance(obj, c_char_p):
            return obj

        # Convert from POINTER(c_char)
        elif isinstance(obj, POINTER(c_char)):
            return obj

        # Convert from raw pointer
        elif isinstance(obj, int):
            return cls(cast(obj, POINTER(c_char)))

        # Convert from object
        else:
            return String.from_param(obj._as_parameter_)
    from_param = classmethod(from_param)

def ReturnString(obj, func=None, arguments=None):
    return String.from_param(obj)

# As of ctypes 1.0, ctypes does not support custom error-checking
# functions on callbacks, nor does it support custom datatypes on
# callbacks, so we must ensure that all callbacks return
# primitive datatypes.
#
# Non-primitive return values wrapped with UNCHECKED won't be
# typechecked, and will be converted to c_void_p.
def UNCHECKED(type):
    if (hasattr(type, "_type_") and isinstance(type._type_, str)
        and type._type_ != "P"):
        return type
    else:
        return c_void_p

# ctypes doesn't have direct support for variadic functions, so we have to write
# our own wrapper class
class _variadic_function(object):
    def __init__(self,func,restype,argtypes):
        self.func=func
        self.func.restype=restype
        self.argtypes=argtypes
    def _as_parameter_(self):
        # So we can pass this variadic function as a function pointer
        return self.func
    def __call__(self,*args):
        fixed_args=[]
        i=0
        for argtype in self.argtypes:
            # Typecheck what we can
            fixed_args.append(argtype.from_param(args[i]))
            i+=1
        return self.func(*fixed_args+list(args[i:]))

# End preamble

_libs = {}
_libdirs = []

# Begin loader

# ----------------------------------------------------------------------------
# Copyright (c) 2008 David James
# Copyright (c) 2006-2008 Alex Holkner
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of pyglet nor the names of its
#    contributors may be used to endorse or promote products
#    derived from this software without specific prior written
#    permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------------

import os.path, re, sys, glob
import ctypes
import ctypes.util

def _environ_path(name):
    if name in os.environ:
        return os.environ[name].split(":")
    else:
        return []

class LibraryLoader(object):
    def __init__(self):
        self.other_dirs=[]

    def load_library(self,libname):
        """Given the name of a library, load it."""
        paths = self.getpaths(libname)

        for path in paths:
            if os.path.exists(path):
                return self.load(path)

        raise ImportError("%s not found." % libname)

    def load(self,path):
        """Given a path to a library, load it."""
        try:
            # Darwin requires dlopen to be called with mode RTLD_GLOBAL instead
            # of the default RTLD_LOCAL.  Without this, you end up with
            # libraries not being loadable, resulting in "Symbol not found"
            # errors
            if sys.platform == 'darwin':
                return ctypes.CDLL(path, ctypes.RTLD_GLOBAL)
            else:
                return ctypes.cdll.LoadLibrary(path)
        except OSError,e:
            raise ImportError(e)

    def getpaths(self,libname):
        """Return a list of paths where the library might be found."""
        if os.path.isabs(libname):
            yield libname

        else:
            for path in self.getplatformpaths(libname):
                yield path

            path = ctypes.util.find_library(libname)
            if path: yield path

    def getplatformpaths(self, libname):
        return []

# Darwin (Mac OS X)

class DarwinLibraryLoader(LibraryLoader):
    name_formats = ["lib%s.dylib", "lib%s.so", "lib%s.bundle", "%s.dylib",
                "%s.so", "%s.bundle", "%s"]

    def getplatformpaths(self,libname):
        if os.path.pathsep in libname:
            names = [libname]
        else:
            names = [format % libname for format in self.name_formats]

        for dir in self.getdirs(libname):
            for name in names:
                yield os.path.join(dir,name)

    def getdirs(self,libname):
        '''Implements the dylib search as specified in Apple documentation:

        http://developer.apple.com/documentation/DeveloperTools/Conceptual/
            DynamicLibraries/Articles/DynamicLibraryUsageGuidelines.html

        Before commencing the standard search, the method first checks
        the bundle's ``Frameworks`` directory if the application is running
        within a bundle (OS X .app).
        '''

        dyld_fallback_library_path = _environ_path("DYLD_FALLBACK_LIBRARY_PATH")
        if not dyld_fallback_library_path:
            dyld_fallback_library_path = [os.path.expanduser('~/lib'),
                                          '/usr/local/lib', '/usr/lib']

        dirs = []

        if '/' in libname:
            dirs.extend(_environ_path("DYLD_LIBRARY_PATH"))
        else:
            dirs.extend(_environ_path("LD_LIBRARY_PATH"))
            dirs.extend(_environ_path("DYLD_LIBRARY_PATH"))

        dirs.extend(self.other_dirs)
        dirs.append(".")

        if hasattr(sys, 'frozen') and sys.frozen == 'macosx_app':
            dirs.append(os.path.join(
                os.environ['RESOURCEPATH'],
                '..',
                'Frameworks'))

        dirs.extend(dyld_fallback_library_path)

        return dirs

# Posix

class PosixLibraryLoader(LibraryLoader):
    _ld_so_cache = None

    def _create_ld_so_cache(self):
        # Recreate search path followed by ld.so.  This is going to be
        # slow to build, and incorrect (ld.so uses ld.so.cache, which may
        # not be up-to-date).  Used only as fallback for distros without
        # /sbin/ldconfig.
        #
        # We assume the DT_RPATH and DT_RUNPATH binary sections are omitted.

        directories = []
        for name in ("LD_LIBRARY_PATH",
                     "SHLIB_PATH", # HPUX
                     "LIBPATH", # OS/2, AIX
                     "LIBRARY_PATH", # BE/OS
                    ):
            if name in os.environ:
                directories.extend(os.environ[name].split(os.pathsep))
        directories.extend(self.other_dirs)
        directories.append(".")

        try: directories.extend([dir.strip() for dir in open('/etc/ld.so.conf')])
        except IOError: pass

        directories.extend(['/lib', '/usr/lib', '/lib64', '/usr/lib64'])

        cache = {}
        lib_re = re.compile(r'lib(.*)\.s[ol]')
        ext_re = re.compile(r'\.s[ol]$')
        for dir in directories:
            try:
                for path in glob.glob("%s/*.s[ol]*" % dir):
                    file = os.path.basename(path)

                    # Index by filename
                    if file not in cache:
                        cache[file] = path

                    # Index by library name
                    match = lib_re.match(file)
                    if match:
                        library = match.group(1)
                        if library not in cache:
                            cache[library] = path
            except OSError:
                pass

        self._ld_so_cache = cache

    def getplatformpaths(self, libname):
        if self._ld_so_cache is None:
            self._create_ld_so_cache()

        result = self._ld_so_cache.get(libname)
        if result: yield result

        path = ctypes.util.find_library(libname)
        if path: yield os.path.join("/lib",path)

# Windows

class _WindowsLibrary(object):
    def __init__(self, path):
        self.cdll = ctypes.cdll.LoadLibrary(path)
        self.windll = ctypes.windll.LoadLibrary(path)

    def __getattr__(self, name):
        try: return getattr(self.cdll,name)
        except AttributeError:
            try: return getattr(self.windll,name)
            except AttributeError:
                raise

class WindowsLibraryLoader(LibraryLoader):
    name_formats = ["%s.dll", "lib%s.dll", "%slib.dll"]

    def load_library(self, libname):
        try:
            result = LibraryLoader.load_library(self, libname)
        except ImportError:
            result = None
            if os.path.sep not in libname:
                for name in self.name_formats:
                    try:
                        result = getattr(ctypes.cdll, name % libname)
                        if result:
                            break
                    except WindowsError:
                        result = None
            if result is None:
                try:
                    result = getattr(ctypes.cdll, libname)
                except WindowsError:
                    result = None
            if result is None:
                raise ImportError("%s not found." % libname)
        return result

    def load(self, path):
        return _WindowsLibrary(path)

    def getplatformpaths(self, libname):
        if os.path.sep not in libname:
            for name in self.name_formats:
                dll_in_current_dir = os.path.abspath(name % libname)
                if os.path.exists(dll_in_current_dir):
                    yield dll_in_current_dir
                path = ctypes.util.find_library(name % libname)
                if path:
                    yield path

# Platform switching

# If your value of sys.platform does not appear in this dict, please contact
# the Ctypesgen maintainers.

loaderclass = {
    "darwin":   DarwinLibraryLoader,
    "cygwin":   WindowsLibraryLoader,
    "win32":    WindowsLibraryLoader
}

loader = loaderclass.get(sys.platform, PosixLibraryLoader)()

def add_library_search_dirs(other_dirs):
    loader.other_dirs = other_dirs

load_library = loader.load_library

del loaderclass

# End loader

add_library_search_dirs([])

# Begin libraries

_libs["GSS"] = load_library("GSS")

# 1 libraries
# End libraries

# No modules

__darwin_uid_t = c_uint32 # /usr/include/sys/_types.h: 133

uid_t = __darwin_uid_t # /usr/include/sys/_types/_uid_t.h: 30

OM_uint32 = c_uint32 # /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 89

OM_uint64 = c_uint64 # /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 90

gss_uint32 = c_uint32 # /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 92

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 94
class struct_gss_name_t_desc_struct(Structure):
    _pack_ = 2
    pass

gss_name_t = POINTER(struct_gss_name_t_desc_struct) # /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 95

gss_const_name_t = POINTER(struct_gss_name_t_desc_struct) # /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 96

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 98
class struct_gss_ctx_id_t_desc_struct(Structure):
    _pack_ = 2
    pass

gss_ctx_id_t = POINTER(struct_gss_ctx_id_t_desc_struct) # /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 99

gss_const_ctx_id_t = struct_gss_ctx_id_t_desc_struct # /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 100

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 105
class struct_gss_OID_desc_struct(Structure):
    _pack_ = 2
    pass

struct_gss_OID_desc_struct.__slots__ = [
    'length',
    'elements',
]
struct_gss_OID_desc_struct._fields_ = [
    ('length', OM_uint32),
    ('elements', POINTER(None)),
]

gss_OID_desc = struct_gss_OID_desc_struct # /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 105

gss_OID = POINTER(struct_gss_OID_desc_struct) # /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 105

gss_const_OID = POINTER(gss_OID_desc) # /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 106

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 111
class struct_gss_OID_set_desc_struct(Structure):
    _pack_ = 2
    pass

struct_gss_OID_set_desc_struct.__slots__ = [
    'count',
    'elements',
]
struct_gss_OID_set_desc_struct._fields_ = [
    ('count', c_size_t),
    ('elements', gss_OID),
]

gss_OID_set_desc = struct_gss_OID_set_desc_struct # /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 111

gss_OID_set = POINTER(struct_gss_OID_set_desc_struct) # /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 111

gss_const_OID_set = POINTER(gss_OID_set_desc) # /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 112

gss_cred_usage_t = c_int # /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 114

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 116
class struct_gss_cred_id_t_desc_struct(Structure):
    _pack_ = 2
    pass

gss_cred_id_t = POINTER(struct_gss_cred_id_t_desc_struct) # /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 117

gss_const_cred_id_t = POINTER(struct_gss_cred_id_t_desc_struct) # /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 118

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 123
class struct_gss_buffer_desc_struct(Structure):
    _pack_ = 2
    pass

struct_gss_buffer_desc_struct.__slots__ = [
    'length',
    'value',
]
struct_gss_buffer_desc_struct._fields_ = [
    ('length', c_size_t),
    ('value', POINTER(None)),
]

gss_buffer_desc = struct_gss_buffer_desc_struct # /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 123

gss_buffer_t = POINTER(struct_gss_buffer_desc_struct) # /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 123

gss_const_buffer_t = POINTER(gss_buffer_desc) # /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 124

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 126
class struct_gss_channel_bindings_struct(Structure):
    _pack_ = 2
    pass

struct_gss_channel_bindings_struct.__slots__ = [
    'initiator_addrtype',
    'initiator_address',
    'acceptor_addrtype',
    'acceptor_address',
    'application_data',
]
struct_gss_channel_bindings_struct._fields_ = [
    ('initiator_addrtype', OM_uint32),
    ('initiator_address', gss_buffer_desc),
    ('acceptor_addrtype', OM_uint32),
    ('acceptor_address', gss_buffer_desc),
    ('application_data', gss_buffer_desc),
]

gss_channel_bindings_t = POINTER(struct_gss_channel_bindings_struct) # /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 132

gss_const_channel_bindings_t = POINTER(struct_gss_channel_bindings_struct) # /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 133

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 139
class struct_gss_buffer_set_desc_struct(Structure):
    _pack_ = 2
    pass

struct_gss_buffer_set_desc_struct.__slots__ = [
    'count',
    'elements',
]
struct_gss_buffer_set_desc_struct._fields_ = [
    ('count', c_size_t),
    ('elements', POINTER(gss_buffer_desc)),
]

gss_buffer_set_desc = struct_gss_buffer_set_desc_struct # /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 139

gss_buffer_set_t = POINTER(struct_gss_buffer_set_desc_struct) # /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 139

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 144
class struct_gss_iov_buffer_desc_struct(Structure):
    _pack_ = 2
    pass

struct_gss_iov_buffer_desc_struct.__slots__ = [
    'type',
    'buffer',
]
struct_gss_iov_buffer_desc_struct._fields_ = [
    ('type', OM_uint32),
    ('buffer', gss_buffer_desc),
]

gss_iov_buffer_desc = struct_gss_iov_buffer_desc_struct # /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 144

gss_iov_buffer_t = POINTER(struct_gss_iov_buffer_desc_struct) # /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 144

gss_qop_t = OM_uint32 # /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 149

gss_status_id_t = POINTER(OM_uint32) # /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 152

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 153
class struct_gss_auth_identity(Structure):
    _pack_ = 2
    pass

gss_auth_identity_t = POINTER(struct_gss_auth_identity) # /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 153

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 285
class struct_krb5_ccache_data(Structure):
    _pack_ = 2
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 9
try:
    __gss_krb5_copy_ccache_x_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_krb5_copy_ccache_x_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 12
try:
    __gss_krb5_get_tkt_flags_x_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_krb5_get_tkt_flags_x_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 15
try:
    __gss_krb5_extract_authz_data_from_sec_context_x_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_krb5_extract_authz_data_from_sec_context_x_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 18
try:
    __gss_krb5_compat_des3_mic_x_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_krb5_compat_des3_mic_x_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 21
try:
    __gss_krb5_register_acceptor_identity_x_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_krb5_register_acceptor_identity_x_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 24
try:
    __gss_krb5_export_lucid_context_x_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_krb5_export_lucid_context_x_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 27
try:
    __gss_krb5_export_lucid_context_v1_x_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_krb5_export_lucid_context_v1_x_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 30
try:
    __gss_krb5_set_dns_canonicalize_x_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_krb5_set_dns_canonicalize_x_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 33
try:
    __gss_krb5_get_subkey_x_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_krb5_get_subkey_x_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 36
try:
    __gss_krb5_get_initiator_subkey_x_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_krb5_get_initiator_subkey_x_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 39
try:
    __gss_krb5_get_acceptor_subkey_x_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_krb5_get_acceptor_subkey_x_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 42
try:
    __gss_krb5_send_to_kdc_x_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_krb5_send_to_kdc_x_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 45
try:
    __gss_krb5_get_authtime_x_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_krb5_get_authtime_x_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 48
try:
    __gss_krb5_get_service_keyblock_x_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_krb5_get_service_keyblock_x_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 51
try:
    __gss_krb5_set_allowable_enctypes_x_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_krb5_set_allowable_enctypes_x_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 54
try:
    __gss_krb5_set_default_realm_x_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_krb5_set_default_realm_x_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 57
try:
    __gss_krb5_ccache_name_x_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_krb5_ccache_name_x_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 60
try:
    __gss_krb5_set_time_offset_x_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_krb5_set_time_offset_x_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 63
try:
    __gss_krb5_get_time_offset_x_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_krb5_get_time_offset_x_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 66
try:
    __gss_krb5_plugin_register_x_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_krb5_plugin_register_x_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 69
try:
    __gss_ntlm_get_session_key_x_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_ntlm_get_session_key_x_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 72
try:
    __gss_c_nt_ntlm_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_c_nt_ntlm_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 75
try:
    __gss_c_nt_dn_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_c_nt_dn_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 78
try:
    __gss_krb5_nt_principal_name_referral_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_krb5_nt_principal_name_referral_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 81
try:
    __gss_c_ntlm_guest_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_c_ntlm_guest_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 84
try:
    __gss_c_ntlm_v1_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_c_ntlm_v1_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 87
try:
    __gss_c_ntlm_v2_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_c_ntlm_v2_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 90
try:
    __gss_c_ntlm_session_key_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_c_ntlm_session_key_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 93
try:
    __gss_c_ntlm_force_v1_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_c_ntlm_force_v1_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 96
try:
    __gss_krb5_cred_no_ci_flags_x_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_krb5_cred_no_ci_flags_x_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 99
try:
    __gss_c_nt_uuid_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_c_nt_uuid_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 102
try:
    __gss_c_ntlm_support_channelbindings_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_c_ntlm_support_channelbindings_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 105
try:
    __gss_c_ntlm_support_lm2_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_c_ntlm_support_lm2_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 108
try:
    __gss_krb5_import_cred_x_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_krb5_import_cred_x_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 112
for _lib in _libs.values():
    try:
        __gss_c_ntlm_reset_keys_oid_desc = (gss_OID_desc).in_dll(_lib, '__gss_c_ntlm_reset_keys_oid_desc')
        break
    except:
        pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 115
try:
    __gss_c_cred_diag_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_c_cred_diag_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 118
for _lib in _libs.values():
    try:
        __gss_c_cred_validate_oid_desc = (gss_OID_desc).in_dll(_lib, '__gss_c_cred_validate_oid_desc')
        break
    except:
        pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 121
for _lib in _libs.values():
    try:
        __gss_c_cred_set_default_oid_desc = (gss_OID_desc).in_dll(_lib, '__gss_c_cred_set_default_oid_desc')
        break
    except:
        pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 124
for _lib in _libs.values():
    try:
        __gss_c_cred_get_default_oid_desc = (gss_OID_desc).in_dll(_lib, '__gss_c_cred_get_default_oid_desc')
        break
    except:
        pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 127
for _lib in _libs.values():
    try:
        __gss_c_cred_renew_oid_desc = (gss_OID_desc).in_dll(_lib, '__gss_c_cred_renew_oid_desc')
        break
    except:
        pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 131
for _lib in _libs.values():
    try:
        __gss_c_ma_sasl_mech_name_oid_desc = (gss_OID_desc).in_dll(_lib, '__gss_c_ma_sasl_mech_name_oid_desc')
        break
    except:
        pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 134
for _lib in _libs.values():
    try:
        __gss_c_ma_mech_name_oid_desc = (gss_OID_desc).in_dll(_lib, '__gss_c_ma_mech_name_oid_desc')
        break
    except:
        pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 137
for _lib in _libs.values():
    try:
        __gss_c_ma_mech_description_oid_desc = (gss_OID_desc).in_dll(_lib, '__gss_c_ma_mech_description_oid_desc')
        break
    except:
        pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 141
for _lib in _libs.values():
    try:
        __gss_c_cred_password_oid_desc = (gss_OID_desc).in_dll(_lib, '__gss_c_cred_password_oid_desc')
        break
    except:
        pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 144
for _lib in _libs.values():
    try:
        __gss_c_cred_certificate_oid_desc = (gss_OID_desc).in_dll(_lib, '__gss_c_cred_certificate_oid_desc')
        break
    except:
        pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 147
for _lib in _libs.values():
    try:
        __gss_c_cred_secidentity_oid_desc = (gss_OID_desc).in_dll(_lib, '__gss_c_cred_secidentity_oid_desc')
        break
    except:
        pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 150
for _lib in _libs.values():
    try:
        __gss_c_cred_heimbase_oid_desc = (gss_OID_desc).in_dll(_lib, '__gss_c_cred_heimbase_oid_desc')
        break
    except:
        pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 154
try:
    __gss_sasl_digest_md5_mechanism_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_sasl_digest_md5_mechanism_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 157
try:
    __gss_netlogon_mechanism_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_netlogon_mechanism_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 160
try:
    __gss_appl_lkdc_supported_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_appl_lkdc_supported_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 164
try:
    __gss_netlogon_set_session_key_x_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_netlogon_set_session_key_x_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 167
try:
    __gss_netlogon_set_sign_algorithm_x_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_netlogon_set_sign_algorithm_x_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 170
try:
    __gss_netlogon_nt_netbios_dns_name_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_netlogon_nt_netbios_dns_name_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 174
try:
    __gss_c_inq_win2k_pac_x_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_c_inq_win2k_pac_x_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 177
try:
    __gss_c_inq_sspi_session_key_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_c_inq_sspi_session_key_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 183
try:
    __gss_krb5_mechanism_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_krb5_mechanism_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 186
try:
    __gss_ntlm_mechanism_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_ntlm_mechanism_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 189
try:
    __gss_spnego_mechanism_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_spnego_mechanism_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 192
try:
    __gss_iakerb_mechanism_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_iakerb_mechanism_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 195
try:
    __gss_pku2u_mechanism_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_pku2u_mechanism_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 199
try:
    __gss_c_peer_has_updated_spnego_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_c_peer_has_updated_spnego_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 208
for _lib in _libs.values():
    try:
        __gss_c_ma_mech_concrete_oid_desc = (gss_OID_desc).in_dll(_lib, '__gss_c_ma_mech_concrete_oid_desc')
        break
    except:
        pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 211
for _lib in _libs.values():
    try:
        __gss_c_ma_mech_pseudo_oid_desc = (gss_OID_desc).in_dll(_lib, '__gss_c_ma_mech_pseudo_oid_desc')
        break
    except:
        pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 214
for _lib in _libs.values():
    try:
        __gss_c_ma_mech_composite_oid_desc = (gss_OID_desc).in_dll(_lib, '__gss_c_ma_mech_composite_oid_desc')
        break
    except:
        pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 217
for _lib in _libs.values():
    try:
        __gss_c_ma_mech_nego_oid_desc = (gss_OID_desc).in_dll(_lib, '__gss_c_ma_mech_nego_oid_desc')
        break
    except:
        pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 220
for _lib in _libs.values():
    try:
        __gss_c_ma_mech_glue_oid_desc = (gss_OID_desc).in_dll(_lib, '__gss_c_ma_mech_glue_oid_desc')
        break
    except:
        pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 223
for _lib in _libs.values():
    try:
        __gss_c_ma_not_mech_oid_desc = (gss_OID_desc).in_dll(_lib, '__gss_c_ma_not_mech_oid_desc')
        break
    except:
        pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 226
for _lib in _libs.values():
    try:
        __gss_c_ma_deprecated_oid_desc = (gss_OID_desc).in_dll(_lib, '__gss_c_ma_deprecated_oid_desc')
        break
    except:
        pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 229
for _lib in _libs.values():
    try:
        __gss_c_ma_not_dflt_mech_oid_desc = (gss_OID_desc).in_dll(_lib, '__gss_c_ma_not_dflt_mech_oid_desc')
        break
    except:
        pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 232
for _lib in _libs.values():
    try:
        __gss_c_ma_itok_framed_oid_desc = (gss_OID_desc).in_dll(_lib, '__gss_c_ma_itok_framed_oid_desc')
        break
    except:
        pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 235
for _lib in _libs.values():
    try:
        __gss_c_ma_auth_init_oid_desc = (gss_OID_desc).in_dll(_lib, '__gss_c_ma_auth_init_oid_desc')
        break
    except:
        pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 238
for _lib in _libs.values():
    try:
        __gss_c_ma_auth_targ_oid_desc = (gss_OID_desc).in_dll(_lib, '__gss_c_ma_auth_targ_oid_desc')
        break
    except:
        pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 241
for _lib in _libs.values():
    try:
        __gss_c_ma_auth_init_init_oid_desc = (gss_OID_desc).in_dll(_lib, '__gss_c_ma_auth_init_init_oid_desc')
        break
    except:
        pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 244
for _lib in _libs.values():
    try:
        __gss_c_ma_auth_targ_init_oid_desc = (gss_OID_desc).in_dll(_lib, '__gss_c_ma_auth_targ_init_oid_desc')
        break
    except:
        pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 247
for _lib in _libs.values():
    try:
        __gss_c_ma_auth_init_anon_oid_desc = (gss_OID_desc).in_dll(_lib, '__gss_c_ma_auth_init_anon_oid_desc')
        break
    except:
        pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 250
for _lib in _libs.values():
    try:
        __gss_c_ma_auth_targ_anon_oid_desc = (gss_OID_desc).in_dll(_lib, '__gss_c_ma_auth_targ_anon_oid_desc')
        break
    except:
        pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 253
for _lib in _libs.values():
    try:
        __gss_c_ma_deleg_cred_oid_desc = (gss_OID_desc).in_dll(_lib, '__gss_c_ma_deleg_cred_oid_desc')
        break
    except:
        pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 256
for _lib in _libs.values():
    try:
        __gss_c_ma_integ_prot_oid_desc = (gss_OID_desc).in_dll(_lib, '__gss_c_ma_integ_prot_oid_desc')
        break
    except:
        pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 259
for _lib in _libs.values():
    try:
        __gss_c_ma_conf_prot_oid_desc = (gss_OID_desc).in_dll(_lib, '__gss_c_ma_conf_prot_oid_desc')
        break
    except:
        pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 262
for _lib in _libs.values():
    try:
        __gss_c_ma_mic_oid_desc = (gss_OID_desc).in_dll(_lib, '__gss_c_ma_mic_oid_desc')
        break
    except:
        pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 265
for _lib in _libs.values():
    try:
        __gss_c_ma_wrap_oid_desc = (gss_OID_desc).in_dll(_lib, '__gss_c_ma_wrap_oid_desc')
        break
    except:
        pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 268
for _lib in _libs.values():
    try:
        __gss_c_ma_prot_ready_oid_desc = (gss_OID_desc).in_dll(_lib, '__gss_c_ma_prot_ready_oid_desc')
        break
    except:
        pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 271
for _lib in _libs.values():
    try:
        __gss_c_ma_replay_det_oid_desc = (gss_OID_desc).in_dll(_lib, '__gss_c_ma_replay_det_oid_desc')
        break
    except:
        pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 274
for _lib in _libs.values():
    try:
        __gss_c_ma_oos_det_oid_desc = (gss_OID_desc).in_dll(_lib, '__gss_c_ma_oos_det_oid_desc')
        break
    except:
        pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 277
for _lib in _libs.values():
    try:
        __gss_c_ma_cbindings_oid_desc = (gss_OID_desc).in_dll(_lib, '__gss_c_ma_cbindings_oid_desc')
        break
    except:
        pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 280
for _lib in _libs.values():
    try:
        __gss_c_ma_pfs_oid_desc = (gss_OID_desc).in_dll(_lib, '__gss_c_ma_pfs_oid_desc')
        break
    except:
        pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 283
for _lib in _libs.values():
    try:
        __gss_c_ma_compress_oid_desc = (gss_OID_desc).in_dll(_lib, '__gss_c_ma_compress_oid_desc')
        break
    except:
        pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 286
for _lib in _libs.values():
    try:
        __gss_c_ma_ctx_trans_oid_desc = (gss_OID_desc).in_dll(_lib, '__gss_c_ma_ctx_trans_oid_desc')
        break
    except:
        pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 71
if hasattr(_libs['GSS'], 'gss_accept_sec_context'):
    gss_accept_sec_context = _libs['GSS'].gss_accept_sec_context
    gss_accept_sec_context.argtypes = [POINTER(OM_uint32), POINTER(gss_ctx_id_t), gss_cred_id_t, gss_buffer_t, gss_channel_bindings_t, POINTER(gss_name_t), POINTER(gss_OID), gss_buffer_t, POINTER(OM_uint32), POINTER(OM_uint32), POINTER(gss_cred_id_t)]
    gss_accept_sec_context.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 85
if hasattr(_libs['GSS'], 'gss_acquire_cred'):
    gss_acquire_cred = _libs['GSS'].gss_acquire_cred
    gss_acquire_cred.argtypes = [POINTER(OM_uint32), gss_name_t, OM_uint32, gss_OID_set, gss_cred_usage_t, POINTER(gss_cred_id_t), POINTER(gss_OID_set), POINTER(OM_uint32)]
    gss_acquire_cred.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 96
if hasattr(_libs['GSS'], 'gss_acquire_cred_with_password'):
    gss_acquire_cred_with_password = _libs['GSS'].gss_acquire_cred_with_password
    gss_acquire_cred_with_password.argtypes = [POINTER(OM_uint32), gss_name_t, gss_buffer_t, OM_uint32, gss_OID_set, gss_cred_usage_t, POINTER(gss_cred_id_t), POINTER(gss_OID_set), POINTER(OM_uint32)]
    gss_acquire_cred_with_password.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 108
if hasattr(_libs['GSS'], 'gss_add_buffer_set_member'):
    gss_add_buffer_set_member = _libs['GSS'].gss_add_buffer_set_member
    gss_add_buffer_set_member.argtypes = [POINTER(OM_uint32), gss_buffer_t, POINTER(gss_buffer_set_t)]
    gss_add_buffer_set_member.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 114
if hasattr(_libs['GSS'], 'gss_add_cred'):
    gss_add_cred = _libs['GSS'].gss_add_cred
    gss_add_cred.argtypes = [POINTER(OM_uint32), gss_cred_id_t, gss_name_t, gss_OID, gss_cred_usage_t, OM_uint32, OM_uint32, POINTER(gss_cred_id_t), POINTER(gss_OID_set), POINTER(OM_uint32), POINTER(OM_uint32)]
    gss_add_cred.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 145
if hasattr(_libs['GSS'], 'gss_add_oid_set_member'):
    gss_add_oid_set_member = _libs['GSS'].gss_add_oid_set_member
    gss_add_oid_set_member.argtypes = [POINTER(OM_uint32), gss_const_OID, POINTER(gss_OID_set)]
    gss_add_oid_set_member.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 174
if hasattr(_libs['GSS'], 'gss_canonicalize_name'):
    gss_canonicalize_name = _libs['GSS'].gss_canonicalize_name
    gss_canonicalize_name.argtypes = [POINTER(OM_uint32), gss_name_t, gss_OID, POINTER(gss_name_t)]
    gss_canonicalize_name.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 181
if hasattr(_libs['GSS'], 'gss_compare_name'):
    gss_compare_name = _libs['GSS'].gss_compare_name
    gss_compare_name.argtypes = [POINTER(OM_uint32), gss_name_t, gss_name_t, POINTER(c_int)]
    gss_compare_name.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 188
if hasattr(_libs['GSS'], 'gss_context_time'):
    gss_context_time = _libs['GSS'].gss_context_time
    gss_context_time.argtypes = [POINTER(OM_uint32), gss_ctx_id_t, POINTER(OM_uint32)]
    gss_context_time.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 194
if hasattr(_libs['GSS'], 'gss_create_empty_buffer_set'):
    gss_create_empty_buffer_set = _libs['GSS'].gss_create_empty_buffer_set
    gss_create_empty_buffer_set.argtypes = [POINTER(OM_uint32), POINTER(gss_buffer_set_t)]
    gss_create_empty_buffer_set.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 199
if hasattr(_libs['GSS'], 'gss_create_empty_oid_set'):
    gss_create_empty_oid_set = _libs['GSS'].gss_create_empty_oid_set
    gss_create_empty_oid_set.argtypes = [POINTER(OM_uint32), POINTER(gss_OID_set)]
    gss_create_empty_oid_set.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 204
if hasattr(_libs['GSS'], 'gss_decapsulate_token'):
    gss_decapsulate_token = _libs['GSS'].gss_decapsulate_token
    gss_decapsulate_token.argtypes = [gss_const_buffer_t, gss_const_OID, gss_buffer_t]
    gss_decapsulate_token.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 210
if hasattr(_libs['GSS'], 'gss_delete_sec_context'):
    gss_delete_sec_context = _libs['GSS'].gss_delete_sec_context
    gss_delete_sec_context.argtypes = [POINTER(OM_uint32), POINTER(gss_ctx_id_t), gss_buffer_t]
    gss_delete_sec_context.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 229
if hasattr(_libs['GSS'], 'gss_destroy_cred'):
    gss_destroy_cred = _libs['GSS'].gss_destroy_cred
    gss_destroy_cred.argtypes = [POINTER(OM_uint32), POINTER(gss_cred_id_t)]
    gss_destroy_cred.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 245
if hasattr(_libs['GSS'], 'gss_display_mech_attr'):
    gss_display_mech_attr = _libs['GSS'].gss_display_mech_attr
    gss_display_mech_attr.argtypes = [POINTER(OM_uint32), gss_const_OID, gss_buffer_t, gss_buffer_t, gss_buffer_t]
    gss_display_mech_attr.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 253
if hasattr(_libs['GSS'], 'gss_display_name'):
    gss_display_name = _libs['GSS'].gss_display_name
    gss_display_name.argtypes = [POINTER(OM_uint32), gss_name_t, gss_buffer_t, POINTER(gss_OID)]
    gss_display_name.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 260
if hasattr(_libs['GSS'], 'gss_display_status'):
    gss_display_status = _libs['GSS'].gss_display_status
    gss_display_status.argtypes = [POINTER(OM_uint32), OM_uint32, c_int, gss_OID, POINTER(OM_uint32), gss_buffer_t]
    gss_display_status.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 269
if hasattr(_libs['GSS'], 'gss_duplicate_name'):
    gss_duplicate_name = _libs['GSS'].gss_duplicate_name
    gss_duplicate_name.argtypes = [POINTER(OM_uint32), gss_name_t, POINTER(gss_name_t)]
    gss_duplicate_name.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 275
if hasattr(_libs['GSS'], 'gss_duplicate_oid'):
    gss_duplicate_oid = _libs['GSS'].gss_duplicate_oid
    gss_duplicate_oid.argtypes = [POINTER(OM_uint32), gss_OID, POINTER(gss_OID)]
    gss_duplicate_oid.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 281
if hasattr(_libs['GSS'], 'gss_encapsulate_token'):
    gss_encapsulate_token = _libs['GSS'].gss_encapsulate_token
    gss_encapsulate_token.argtypes = [gss_const_buffer_t, gss_const_OID, gss_buffer_t]
    gss_encapsulate_token.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 287
if hasattr(_libs['GSS'], 'gss_export_cred'):
    gss_export_cred = _libs['GSS'].gss_export_cred
    gss_export_cred.argtypes = [POINTER(OM_uint32), gss_cred_id_t, gss_buffer_t]
    gss_export_cred.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 293
if hasattr(_libs['GSS'], 'gss_export_name'):
    gss_export_name = _libs['GSS'].gss_export_name
    gss_export_name.argtypes = [POINTER(OM_uint32), gss_name_t, gss_buffer_t]
    gss_export_name.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 299
if hasattr(_libs['GSS'], 'gss_export_sec_context'):
    gss_export_sec_context = _libs['GSS'].gss_export_sec_context
    gss_export_sec_context.argtypes = [POINTER(OM_uint32), POINTER(gss_ctx_id_t), gss_buffer_t]
    gss_export_sec_context.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 305
if hasattr(_libs['GSS'], 'gss_get_mic'):
    gss_get_mic = _libs['GSS'].gss_get_mic
    gss_get_mic.argtypes = [POINTER(OM_uint32), gss_ctx_id_t, gss_qop_t, gss_buffer_t, gss_buffer_t]
    gss_get_mic.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 313
if hasattr(_libs['GSS'], 'gss_import_cred'):
    gss_import_cred = _libs['GSS'].gss_import_cred
    gss_import_cred.argtypes = [POINTER(OM_uint32), gss_buffer_t, POINTER(gss_cred_id_t)]
    gss_import_cred.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 343
if hasattr(_libs['GSS'], 'gss_import_name'):
    gss_import_name = _libs['GSS'].gss_import_name
    gss_import_name.argtypes = [POINTER(OM_uint32), gss_buffer_t, gss_const_OID, POINTER(gss_name_t)]
    gss_import_name.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 353
if hasattr(_libs['GSS'], 'gss_import_sec_context'):
    gss_import_sec_context = _libs['GSS'].gss_import_sec_context
    gss_import_sec_context.argtypes = [POINTER(OM_uint32), gss_buffer_t, POINTER(gss_ctx_id_t)]
    gss_import_sec_context.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 359
if hasattr(_libs['GSS'], 'gss_indicate_mechs'):
    gss_indicate_mechs = _libs['GSS'].gss_indicate_mechs
    gss_indicate_mechs.argtypes = [POINTER(OM_uint32), POINTER(gss_OID_set)]
    gss_indicate_mechs.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 424
if hasattr(_libs['GSS'], 'gss_init_sec_context'):
    gss_init_sec_context = _libs['GSS'].gss_init_sec_context
    gss_init_sec_context.argtypes = [POINTER(OM_uint32), gss_cred_id_t, POINTER(gss_ctx_id_t), gss_name_t, gss_OID, OM_uint32, OM_uint32, gss_channel_bindings_t, gss_buffer_t, POINTER(gss_OID), gss_buffer_t, POINTER(OM_uint32), POINTER(OM_uint32)]
    gss_init_sec_context.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 453
if hasattr(_libs['GSS'], 'gss_inquire_attrs_for_mech'):
    gss_inquire_attrs_for_mech = _libs['GSS'].gss_inquire_attrs_for_mech
    gss_inquire_attrs_for_mech.argtypes = [POINTER(OM_uint32), gss_const_OID, POINTER(gss_OID_set), POINTER(gss_OID_set)]
    gss_inquire_attrs_for_mech.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 460
if hasattr(_libs['GSS'], 'gss_inquire_context'):
    gss_inquire_context = _libs['GSS'].gss_inquire_context
    gss_inquire_context.argtypes = [POINTER(OM_uint32), gss_ctx_id_t, POINTER(gss_name_t), POINTER(gss_name_t), POINTER(OM_uint32), POINTER(gss_OID), POINTER(OM_uint32), POINTER(c_int), POINTER(c_int)]
    gss_inquire_context.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 472
if hasattr(_libs['GSS'], 'gss_inquire_cred'):
    gss_inquire_cred = _libs['GSS'].gss_inquire_cred
    gss_inquire_cred.argtypes = [POINTER(OM_uint32), gss_cred_id_t, POINTER(gss_name_t), POINTER(OM_uint32), POINTER(gss_cred_usage_t), POINTER(gss_OID_set)]
    gss_inquire_cred.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 481
if hasattr(_libs['GSS'], 'gss_inquire_cred_by_mech'):
    gss_inquire_cred_by_mech = _libs['GSS'].gss_inquire_cred_by_mech
    gss_inquire_cred_by_mech.argtypes = [POINTER(OM_uint32), gss_cred_id_t, gss_OID, POINTER(gss_name_t), POINTER(OM_uint32), POINTER(OM_uint32), POINTER(gss_cred_usage_t)]
    gss_inquire_cred_by_mech.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 491
if hasattr(_libs['GSS'], 'gss_inquire_cred_by_oid'):
    gss_inquire_cred_by_oid = _libs['GSS'].gss_inquire_cred_by_oid
    gss_inquire_cred_by_oid.argtypes = [POINTER(OM_uint32), gss_cred_id_t, gss_OID, POINTER(gss_buffer_set_t)]
    gss_inquire_cred_by_oid.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 498
if hasattr(_libs['GSS'], 'gss_inquire_mechs_for_name'):
    gss_inquire_mechs_for_name = _libs['GSS'].gss_inquire_mechs_for_name
    gss_inquire_mechs_for_name.argtypes = [POINTER(OM_uint32), gss_name_t, POINTER(gss_OID_set)]
    gss_inquire_mechs_for_name.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 504
if hasattr(_libs['GSS'], 'gss_inquire_names_for_mech'):
    gss_inquire_names_for_mech = _libs['GSS'].gss_inquire_names_for_mech
    gss_inquire_names_for_mech.argtypes = [POINTER(OM_uint32), gss_const_OID, POINTER(gss_OID_set)]
    gss_inquire_names_for_mech.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 510
if hasattr(_libs['GSS'], 'gss_inquire_sec_context_by_oid'):
    gss_inquire_sec_context_by_oid = _libs['GSS'].gss_inquire_sec_context_by_oid
    gss_inquire_sec_context_by_oid.argtypes = [POINTER(OM_uint32), gss_ctx_id_t, gss_OID, POINTER(gss_buffer_set_t)]
    gss_inquire_sec_context_by_oid.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 547
if hasattr(_libs['GSS'], 'gss_iter_creds_f'):
    gss_iter_creds_f = _libs['GSS'].gss_iter_creds_f
    gss_iter_creds_f.argtypes = [POINTER(OM_uint32), OM_uint32, gss_const_OID, POINTER(None), CFUNCTYPE(UNCHECKED(None), POINTER(None), gss_OID, gss_cred_id_t)]
    gss_iter_creds_f.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 555
if hasattr(_libs['GSS'], 'gss_krb5_ccache_name'):
    gss_krb5_ccache_name = _libs['GSS'].gss_krb5_ccache_name
    gss_krb5_ccache_name.argtypes = [POINTER(OM_uint32), String, POINTER(POINTER(c_char))]
    gss_krb5_ccache_name.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 561
if hasattr(_libs['GSS'], 'gss_krb5_copy_ccache'):
    gss_krb5_copy_ccache = _libs['GSS'].gss_krb5_copy_ccache
    gss_krb5_copy_ccache.argtypes = [POINTER(OM_uint32), gss_cred_id_t, POINTER(struct_krb5_ccache_data)]
    gss_krb5_copy_ccache.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 567
if hasattr(_libs['GSS'], 'gss_krb5_export_lucid_sec_context'):
    gss_krb5_export_lucid_sec_context = _libs['GSS'].gss_krb5_export_lucid_sec_context
    gss_krb5_export_lucid_sec_context.argtypes = [POINTER(OM_uint32), POINTER(gss_ctx_id_t), OM_uint32, POINTER(POINTER(None))]
    gss_krb5_export_lucid_sec_context.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 574
if hasattr(_libs['GSS'], 'gss_krb5_free_lucid_sec_context'):
    gss_krb5_free_lucid_sec_context = _libs['GSS'].gss_krb5_free_lucid_sec_context
    gss_krb5_free_lucid_sec_context.argtypes = [POINTER(OM_uint32), POINTER(None)]
    gss_krb5_free_lucid_sec_context.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 579
if hasattr(_libs['GSS'], 'gss_krb5_set_allowable_enctypes'):
    gss_krb5_set_allowable_enctypes = _libs['GSS'].gss_krb5_set_allowable_enctypes
    gss_krb5_set_allowable_enctypes.argtypes = [POINTER(OM_uint32), gss_cred_id_t, OM_uint32, POINTER(c_int32)]
    gss_krb5_set_allowable_enctypes.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 599
if hasattr(_libs['GSS'], 'gss_oid_equal'):
    gss_oid_equal = _libs['GSS'].gss_oid_equal
    gss_oid_equal.argtypes = [gss_const_OID, gss_const_OID]
    gss_oid_equal.restype = c_int

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 604
if hasattr(_libs['GSS'], 'gss_oid_to_str'):
    gss_oid_to_str = _libs['GSS'].gss_oid_to_str
    gss_oid_to_str.argtypes = [POINTER(OM_uint32), gss_OID, gss_buffer_t]
    gss_oid_to_str.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 610
if hasattr(_libs['GSS'], 'gss_process_context_token'):
    gss_process_context_token = _libs['GSS'].gss_process_context_token
    gss_process_context_token.argtypes = [POINTER(OM_uint32), gss_ctx_id_t, gss_buffer_t]
    gss_process_context_token.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 616
if hasattr(_libs['GSS'], 'gss_pseudo_random'):
    gss_pseudo_random = _libs['GSS'].gss_pseudo_random
    gss_pseudo_random.argtypes = [POINTER(OM_uint32), gss_ctx_id_t, c_int, gss_buffer_t, c_ptrdiff_t, gss_buffer_t]
    gss_pseudo_random.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 625
if hasattr(_libs['GSS'], 'gss_release_buffer'):
    gss_release_buffer = _libs['GSS'].gss_release_buffer
    gss_release_buffer.argtypes = [POINTER(OM_uint32), gss_buffer_t]
    gss_release_buffer.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 630
if hasattr(_libs['GSS'], 'gss_release_buffer_set'):
    gss_release_buffer_set = _libs['GSS'].gss_release_buffer_set
    gss_release_buffer_set.argtypes = [POINTER(OM_uint32), POINTER(gss_buffer_set_t)]
    gss_release_buffer_set.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 656
if hasattr(_libs['GSS'], 'gss_release_cred'):
    gss_release_cred = _libs['GSS'].gss_release_cred
    gss_release_cred.argtypes = [POINTER(OM_uint32), POINTER(gss_cred_id_t)]
    gss_release_cred.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 676
if hasattr(_libs['GSS'], 'gss_release_name'):
    gss_release_name = _libs['GSS'].gss_release_name
    gss_release_name.argtypes = [POINTER(OM_uint32), POINTER(gss_name_t)]
    gss_release_name.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 681
if hasattr(_libs['GSS'], 'gss_release_oid'):
    gss_release_oid = _libs['GSS'].gss_release_oid
    gss_release_oid.argtypes = [POINTER(OM_uint32), POINTER(gss_OID)]
    gss_release_oid.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 686
if hasattr(_libs['GSS'], 'gss_release_oid_set'):
    gss_release_oid_set = _libs['GSS'].gss_release_oid_set
    gss_release_oid_set.argtypes = [POINTER(OM_uint32), POINTER(gss_OID_set)]
    gss_release_oid_set.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 691
if hasattr(_libs['GSS'], 'gss_seal'):
    gss_seal = _libs['GSS'].gss_seal
    gss_seal.argtypes = [POINTER(OM_uint32), gss_ctx_id_t, c_int, c_int, gss_buffer_t, POINTER(c_int), gss_buffer_t]
    gss_seal.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 701
if hasattr(_libs['GSS'], 'gss_set_cred_option'):
    gss_set_cred_option = _libs['GSS'].gss_set_cred_option
    gss_set_cred_option.argtypes = [POINTER(OM_uint32), POINTER(gss_cred_id_t), gss_OID, gss_buffer_t]
    gss_set_cred_option.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 708
if hasattr(_libs['GSS'], 'gss_set_sec_context_option'):
    gss_set_sec_context_option = _libs['GSS'].gss_set_sec_context_option
    gss_set_sec_context_option.argtypes = [POINTER(OM_uint32), POINTER(gss_ctx_id_t), gss_OID, gss_buffer_t]
    gss_set_sec_context_option.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 715
if hasattr(_libs['GSS'], 'gss_sign'):
    gss_sign = _libs['GSS'].gss_sign
    gss_sign.argtypes = [POINTER(OM_uint32), gss_ctx_id_t, c_int, gss_buffer_t, gss_buffer_t]
    gss_sign.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 723
if hasattr(_libs['GSS'], 'gss_test_oid_set_member'):
    gss_test_oid_set_member = _libs['GSS'].gss_test_oid_set_member
    gss_test_oid_set_member.argtypes = [POINTER(OM_uint32), gss_const_OID, gss_OID_set, POINTER(c_int)]
    gss_test_oid_set_member.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 730
if hasattr(_libs['GSS'], 'gss_unseal'):
    gss_unseal = _libs['GSS'].gss_unseal
    gss_unseal.argtypes = [POINTER(OM_uint32), gss_ctx_id_t, gss_buffer_t, gss_buffer_t, POINTER(c_int), POINTER(c_int)]
    gss_unseal.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 739
if hasattr(_libs['GSS'], 'gss_unwrap'):
    gss_unwrap = _libs['GSS'].gss_unwrap
    gss_unwrap.argtypes = [POINTER(OM_uint32), gss_ctx_id_t, gss_buffer_t, gss_buffer_t, POINTER(c_int), POINTER(gss_qop_t)]
    gss_unwrap.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 748
if hasattr(_libs['GSS'], 'gss_userok'):
    gss_userok = _libs['GSS'].gss_userok
    gss_userok.argtypes = [gss_name_t, String]
    gss_userok.restype = c_int

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 753
if hasattr(_libs['GSS'], 'gss_verify'):
    gss_verify = _libs['GSS'].gss_verify
    gss_verify.argtypes = [POINTER(OM_uint32), gss_ctx_id_t, gss_buffer_t, gss_buffer_t, POINTER(c_int)]
    gss_verify.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 761
if hasattr(_libs['GSS'], 'gss_verify_mic'):
    gss_verify_mic = _libs['GSS'].gss_verify_mic
    gss_verify_mic.argtypes = [POINTER(OM_uint32), gss_ctx_id_t, gss_buffer_t, gss_buffer_t, POINTER(gss_qop_t)]
    gss_verify_mic.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 783
if hasattr(_libs['GSS'], 'gss_wrap'):
    gss_wrap = _libs['GSS'].gss_wrap
    gss_wrap.argtypes = [POINTER(OM_uint32), gss_ctx_id_t, c_int, gss_qop_t, gss_buffer_t, POINTER(c_int), gss_buffer_t]
    gss_wrap.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 793
if hasattr(_libs['GSS'], 'gss_wrap_size_limit'):
    gss_wrap_size_limit = _libs['GSS'].gss_wrap_size_limit
    gss_wrap_size_limit.argtypes = [POINTER(OM_uint32), gss_ctx_id_t, c_int, gss_qop_t, OM_uint32, POINTER(OM_uint32)]
    gss_wrap_size_limit.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 802
if hasattr(_libs['GSS'], 'gsskrb5_extract_authz_data_from_sec_context'):
    gsskrb5_extract_authz_data_from_sec_context = _libs['GSS'].gsskrb5_extract_authz_data_from_sec_context
    gsskrb5_extract_authz_data_from_sec_context.argtypes = [POINTER(OM_uint32), gss_ctx_id_t, c_int, gss_buffer_t]
    gsskrb5_extract_authz_data_from_sec_context.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 809
if hasattr(_libs['GSS'], 'gsskrb5_register_acceptor_identity'):
    gsskrb5_register_acceptor_identity = _libs['GSS'].gsskrb5_register_acceptor_identity
    gsskrb5_register_acceptor_identity.argtypes = [String]
    gsskrb5_register_acceptor_identity.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_protos.h: 812
if hasattr(_libs['GSS'], 'krb5_gss_register_acceptor_identity'):
    krb5_gss_register_acceptor_identity = _libs['GSS'].krb5_gss_register_acceptor_identity
    krb5_gss_register_acceptor_identity.argtypes = [String]
    krb5_gss_register_acceptor_identity.restype = OM_uint32

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 302
try:
    __gss_c_nt_user_name_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_c_nt_user_name_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 316
try:
    __gss_c_nt_machine_uid_name_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_c_nt_machine_uid_name_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 330
try:
    __gss_c_nt_string_uid_name_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_c_nt_string_uid_name_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 350
try:
    __gss_c_nt_hostbased_service_x_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_c_nt_hostbased_service_x_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 364
try:
    __gss_c_nt_hostbased_service_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_c_nt_hostbased_service_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 377
try:
    __gss_c_nt_anonymous_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_c_nt_anonymous_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 390
try:
    __gss_c_nt_export_name_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_c_nt_export_name_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 397
try:
    __gss_sasl_digest_md5_mechanism_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_sasl_digest_md5_mechanism_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 404
try:
    __gss_c_inq_sspi_session_key_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_c_inq_sspi_session_key_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 412
try:
    __gss_c_inq_win2k_pac_x_oid_desc = (gss_OID_desc).in_dll(_libs['GSS'], '__gss_c_inq_win2k_pac_x_oid_desc')
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 509
for _lib in _libs.values():
    try:
        __gss_c_attr_local_login_user = (gss_buffer_desc).in_dll(_lib, '__gss_c_attr_local_login_user')
        break
    except:
        pass

gss_iter_OID = gss_OID # /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 62

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 158
try:
    GSS_C_DELEG_FLAG = 1
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 159
try:
    GSS_C_MUTUAL_FLAG = 2
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 160
try:
    GSS_C_REPLAY_FLAG = 4
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 161
try:
    GSS_C_SEQUENCE_FLAG = 8
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 162
try:
    GSS_C_CONF_FLAG = 16
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 163
try:
    GSS_C_INTEG_FLAG = 32
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 164
try:
    GSS_C_ANON_FLAG = 64
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 165
try:
    GSS_C_PROT_READY_FLAG = 128
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 166
try:
    GSS_C_TRANS_FLAG = 256
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 168
try:
    GSS_C_DCE_STYLE = 4096
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 169
try:
    GSS_C_IDENTIFY_FLAG = 8192
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 170
try:
    GSS_C_EXTENDED_ERROR_FLAG = 16384
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 171
try:
    GSS_C_DELEG_POLICY_FLAG = 32768
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 176
try:
    GSS_C_BOTH = 0
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 177
try:
    GSS_C_INITIATE = 1
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 178
try:
    GSS_C_ACCEPT = 2
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 180
try:
    GSS_C_OPTION_MASK = 65535
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 181
try:
    GSS_C_CRED_NO_UI = 65536
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 186
try:
    GSS_C_GSS_CODE = 1
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 187
try:
    GSS_C_MECH_CODE = 2
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 192
try:
    GSS_C_AF_UNSPEC = 0
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 193
try:
    GSS_C_AF_LOCAL = 1
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 194
try:
    GSS_C_AF_INET = 2
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 195
try:
    GSS_C_AF_IMPLINK = 3
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 196
try:
    GSS_C_AF_PUP = 4
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 197
try:
    GSS_C_AF_CHAOS = 5
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 198
try:
    GSS_C_AF_NS = 6
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 199
try:
    GSS_C_AF_NBS = 7
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 200
try:
    GSS_C_AF_ECMA = 8
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 201
try:
    GSS_C_AF_DATAKIT = 9
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 202
try:
    GSS_C_AF_CCITT = 10
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 203
try:
    GSS_C_AF_SNA = 11
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 204
try:
    GSS_C_AF_DECnet = 12
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 205
try:
    GSS_C_AF_DLI = 13
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 206
try:
    GSS_C_AF_LAT = 14
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 207
try:
    GSS_C_AF_HYLINK = 15
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 208
try:
    GSS_C_AF_APPLETALK = 16
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 209
try:
    GSS_C_AF_BSC = 17
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 210
try:
    GSS_C_AF_DSS = 18
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 211
try:
    GSS_C_AF_OSI = 19
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 212
try:
    GSS_C_AF_X25 = 21
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 213
try:
    GSS_C_AF_INET6 = 24
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 215
try:
    GSS_C_AF_NULLADDR = 255
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 220
try:
    GSS_C_NO_NAME = 0
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 221
try:
    GSS_C_NO_BUFFER = 0
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 222
try:
    GSS_C_NO_BUFFER_SET = 0
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 223
try:
    GSS_C_NO_OID = 0
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 224
try:
    GSS_C_NO_OID_SET = 0
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 225
try:
    GSS_C_NO_CONTEXT = 0
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 226
try:
    GSS_C_NO_CREDENTIAL = 0
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 227
try:
    GSS_C_NO_CHANNEL_BINDINGS = 0
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 229
try:
    GSS_C_NO_IOV_BUFFER = 0
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 235
try:
    GSS_C_NULL_OID = GSS_C_NO_OID
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 236
try:
    GSS_C_NULL_OID_SET = GSS_C_NO_OID_SET
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 247
try:
    GSS_C_QOP_DEFAULT = 0
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 249
try:
    GSS_KRB5_CONF_C_QOP_DES = 256
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 250
try:
    GSS_KRB5_CONF_C_QOP_DES3_KD = 512
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 256
try:
    GSS_C_INDEFINITE = 4294967295
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 262
try:
    GSS_IOV_BUFFER_TYPE_EMPTY = 0
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 263
try:
    GSS_IOV_BUFFER_TYPE_DATA = 1
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 264
try:
    GSS_IOV_BUFFER_TYPE_HEADER = 2
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 265
try:
    GSS_IOV_BUFFER_TYPE_MECH_PARAMS = 3
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 267
try:
    GSS_IOV_BUFFER_TYPE_TRAILER = 7
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 268
try:
    GSS_IOV_BUFFER_TYPE_PADDING = 9
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 269
try:
    GSS_IOV_BUFFER_TYPE_STREAM = 10
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 270
try:
    GSS_IOV_BUFFER_TYPE_SIGN_ONLY = 11
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 272
try:
    GSS_IOV_BUFFER_TYPE_FLAG_MASK = 4294901760
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 273
try:
    GSS_IOV_BUFFER_FLAG_ALLOCATE = 65536
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 274
try:
    GSS_IOV_BUFFER_FLAG_ALLOCATED = 131072
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 276
try:
    GSS_IOV_BUFFER_TYPE_FLAG_ALLOCATE = 65536
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 277
try:
    GSS_IOV_BUFFER_TYPE_FLAG_ALLOCATED = 131072
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 279
def GSS_IOV_BUFFER_TYPE(_t):
    return (_t & (~GSS_IOV_BUFFER_TYPE_FLAG_MASK))

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 280
def GSS_IOV_BUFFER_FLAGS(_t):
    return (_t & GSS_IOV_BUFFER_TYPE_FLAG_MASK)

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 3
try:
    GSSAPI_GSSAPI_OID = 1
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 10
try:
    GSS_KRB5_COPY_CCACHE_X = pointer(__gss_krb5_copy_ccache_x_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 13
try:
    GSS_KRB5_GET_TKT_FLAGS_X = pointer(__gss_krb5_get_tkt_flags_x_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 16
try:
    GSS_KRB5_EXTRACT_AUTHZ_DATA_FROM_SEC_CONTEXT_X = pointer(__gss_krb5_extract_authz_data_from_sec_context_x_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 19
try:
    GSS_KRB5_COMPAT_DES3_MIC_X = pointer(__gss_krb5_compat_des3_mic_x_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 22
try:
    GSS_KRB5_REGISTER_ACCEPTOR_IDENTITY_X = pointer(__gss_krb5_register_acceptor_identity_x_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 25
try:
    GSS_KRB5_EXPORT_LUCID_CONTEXT_X = pointer(__gss_krb5_export_lucid_context_x_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 28
try:
    GSS_KRB5_EXPORT_LUCID_CONTEXT_V1_X = pointer(__gss_krb5_export_lucid_context_v1_x_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 31
try:
    GSS_KRB5_SET_DNS_CANONICALIZE_X = pointer(__gss_krb5_set_dns_canonicalize_x_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 34
try:
    GSS_KRB5_GET_SUBKEY_X = pointer(__gss_krb5_get_subkey_x_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 37
try:
    GSS_KRB5_GET_INITIATOR_SUBKEY_X = pointer(__gss_krb5_get_initiator_subkey_x_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 40
try:
    GSS_KRB5_GET_ACCEPTOR_SUBKEY_X = pointer(__gss_krb5_get_acceptor_subkey_x_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 43
try:
    GSS_KRB5_SEND_TO_KDC_X = pointer(__gss_krb5_send_to_kdc_x_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 46
try:
    GSS_KRB5_GET_AUTHTIME_X = pointer(__gss_krb5_get_authtime_x_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 49
try:
    GSS_KRB5_GET_SERVICE_KEYBLOCK_X = pointer(__gss_krb5_get_service_keyblock_x_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 52
try:
    GSS_KRB5_SET_ALLOWABLE_ENCTYPES_X = pointer(__gss_krb5_set_allowable_enctypes_x_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 55
try:
    GSS_KRB5_SET_DEFAULT_REALM_X = pointer(__gss_krb5_set_default_realm_x_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 58
try:
    GSS_KRB5_CCACHE_NAME_X = pointer(__gss_krb5_ccache_name_x_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 61
try:
    GSS_KRB5_SET_TIME_OFFSET_X = pointer(__gss_krb5_set_time_offset_x_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 64
try:
    GSS_KRB5_GET_TIME_OFFSET_X = pointer(__gss_krb5_get_time_offset_x_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 67
try:
    GSS_KRB5_PLUGIN_REGISTER_X = pointer(__gss_krb5_plugin_register_x_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 70
try:
    GSS_NTLM_GET_SESSION_KEY_X = pointer(__gss_ntlm_get_session_key_x_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 73
try:
    GSS_C_NT_NTLM = pointer(__gss_c_nt_ntlm_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 76
try:
    GSS_C_NT_DN = pointer(__gss_c_nt_dn_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 79
try:
    GSS_KRB5_NT_PRINCIPAL_NAME_REFERRAL = pointer(__gss_krb5_nt_principal_name_referral_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 82
try:
    GSS_C_NTLM_GUEST = pointer(__gss_c_ntlm_guest_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 85
try:
    GSS_C_NTLM_V1 = pointer(__gss_c_ntlm_v1_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 88
try:
    GSS_C_NTLM_V2 = pointer(__gss_c_ntlm_v2_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 91
try:
    GSS_C_NTLM_SESSION_KEY = pointer(__gss_c_ntlm_session_key_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 94
try:
    GSS_C_NTLM_FORCE_V1 = pointer(__gss_c_ntlm_force_v1_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 97
try:
    GSS_KRB5_CRED_NO_CI_FLAGS_X = pointer(__gss_krb5_cred_no_ci_flags_x_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 100
try:
    GSS_C_NT_UUID = pointer(__gss_c_nt_uuid_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 103
try:
    GSS_C_NTLM_SUPPORT_CHANNELBINDINGS = pointer(__gss_c_ntlm_support_channelbindings_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 106
try:
    GSS_C_NTLM_SUPPORT_LM2 = pointer(__gss_c_ntlm_support_lm2_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 109
try:
    GSS_KRB5_IMPORT_CRED_X = pointer(__gss_krb5_import_cred_x_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 113
try:
    GSS_C_NTLM_RESET_KEYS = pointer(__gss_c_ntlm_reset_keys_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 116
try:
    GSS_C_CRED_DIAG = pointer(__gss_c_cred_diag_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 119
try:
    GSS_C_CRED_VALIDATE = pointer(__gss_c_cred_validate_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 122
try:
    GSS_C_CRED_SET_DEFAULT = pointer(__gss_c_cred_set_default_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 125
try:
    GSS_C_CRED_GET_DEFAULT = pointer(__gss_c_cred_get_default_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 128
try:
    GSS_C_CRED_RENEW = pointer(__gss_c_cred_renew_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 132
try:
    GSS_C_MA_SASL_MECH_NAME = pointer(__gss_c_ma_sasl_mech_name_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 135
try:
    GSS_C_MA_MECH_NAME = pointer(__gss_c_ma_mech_name_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 138
try:
    GSS_C_MA_MECH_DESCRIPTION = pointer(__gss_c_ma_mech_description_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 142
try:
    GSS_C_CRED_PASSWORD = pointer(__gss_c_cred_password_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 145
try:
    GSS_C_CRED_CERTIFICATE = pointer(__gss_c_cred_certificate_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 148
try:
    GSS_C_CRED_SecIdentity = pointer(__gss_c_cred_secidentity_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 151
try:
    GSS_C_CRED_HEIMBASE = pointer(__gss_c_cred_heimbase_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 155
try:
    GSS_SASL_DIGEST_MD5_MECHANISM = pointer(__gss_sasl_digest_md5_mechanism_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 158
try:
    GSS_NETLOGON_MECHANISM = pointer(__gss_netlogon_mechanism_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 161
try:
    GSS_APPL_LKDC_SUPPORTED = pointer(__gss_appl_lkdc_supported_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 165
try:
    GSS_NETLOGON_SET_SESSION_KEY_X = pointer(__gss_netlogon_set_session_key_x_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 168
try:
    GSS_NETLOGON_SET_SIGN_ALGORITHM_X = pointer(__gss_netlogon_set_sign_algorithm_x_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 171
try:
    GSS_NETLOGON_NT_NETBIOS_DNS_NAME = pointer(__gss_netlogon_nt_netbios_dns_name_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 175
try:
    GSS_C_INQ_WIN2K_PAC_X = pointer(__gss_c_inq_win2k_pac_x_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 178
try:
    GSS_C_INQ_SSPI_SESSION_KEY = pointer(__gss_c_inq_sspi_session_key_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 184
try:
    GSS_KRB5_MECHANISM = pointer(__gss_krb5_mechanism_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 187
try:
    GSS_NTLM_MECHANISM = pointer(__gss_ntlm_mechanism_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 190
try:
    GSS_SPNEGO_MECHANISM = pointer(__gss_spnego_mechanism_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 193
try:
    GSS_IAKERB_MECHANISM = pointer(__gss_iakerb_mechanism_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 196
try:
    GSS_PKU2U_MECHANISM = pointer(__gss_pku2u_mechanism_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 200
try:
    GSS_C_PEER_HAS_UPDATED_SPNEGO = pointer(__gss_c_peer_has_updated_spnego_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 209
try:
    GSS_C_MA_MECH_CONCRETE = pointer(__gss_c_ma_mech_concrete_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 212
try:
    GSS_C_MA_MECH_PSEUDO = pointer(__gss_c_ma_mech_pseudo_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 215
try:
    GSS_C_MA_MECH_COMPOSITE = pointer(__gss_c_ma_mech_composite_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 218
try:
    GSS_C_MA_MECH_NEGO = pointer(__gss_c_ma_mech_nego_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 221
try:
    GSS_C_MA_MECH_GLUE = pointer(__gss_c_ma_mech_glue_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 224
try:
    GSS_C_MA_NOT_MECH = pointer(__gss_c_ma_not_mech_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 227
try:
    GSS_C_MA_DEPRECATED = pointer(__gss_c_ma_deprecated_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 230
try:
    GSS_C_MA_NOT_DFLT_MECH = pointer(__gss_c_ma_not_dflt_mech_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 233
try:
    GSS_C_MA_ITOK_FRAMED = pointer(__gss_c_ma_itok_framed_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 236
try:
    GSS_C_MA_AUTH_INIT = pointer(__gss_c_ma_auth_init_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 239
try:
    GSS_C_MA_AUTH_TARG = pointer(__gss_c_ma_auth_targ_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 242
try:
    GSS_C_MA_AUTH_INIT_INIT = pointer(__gss_c_ma_auth_init_init_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 245
try:
    GSS_C_MA_AUTH_TARG_INIT = pointer(__gss_c_ma_auth_targ_init_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 248
try:
    GSS_C_MA_AUTH_INIT_ANON = pointer(__gss_c_ma_auth_init_anon_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 251
try:
    GSS_C_MA_AUTH_TARG_ANON = pointer(__gss_c_ma_auth_targ_anon_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 254
try:
    GSS_C_MA_DELEG_CRED = pointer(__gss_c_ma_deleg_cred_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 257
try:
    GSS_C_MA_INTEG_PROT = pointer(__gss_c_ma_integ_prot_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 260
try:
    GSS_C_MA_CONF_PROT = pointer(__gss_c_ma_conf_prot_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 263
try:
    GSS_C_MA_MIC = pointer(__gss_c_ma_mic_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 266
try:
    GSS_C_MA_WRAP = pointer(__gss_c_ma_wrap_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 269
try:
    GSS_C_MA_PROT_READY = pointer(__gss_c_ma_prot_ready_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 272
try:
    GSS_C_MA_REPLAY_DET = pointer(__gss_c_ma_replay_det_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 275
try:
    GSS_C_MA_OOS_DET = pointer(__gss_c_ma_oos_det_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 278
try:
    GSS_C_MA_CBINDINGS = pointer(__gss_c_ma_cbindings_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 281
try:
    GSS_C_MA_PFS = pointer(__gss_c_ma_pfs_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 284
try:
    GSS_C_MA_COMPRESS = pointer(__gss_c_ma_compress_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi_oid.h: 287
try:
    GSS_C_MA_CTX_TRANS = pointer(__gss_c_ma_ctx_trans_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 303
try:
    GSS_C_NT_USER_NAME = pointer(__gss_c_nt_user_name_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 317
try:
    GSS_C_NT_MACHINE_UID_NAME = pointer(__gss_c_nt_machine_uid_name_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 331
try:
    GSS_C_NT_STRING_UID_NAME = pointer(__gss_c_nt_string_uid_name_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 351
try:
    GSS_C_NT_HOSTBASED_SERVICE_X = pointer(__gss_c_nt_hostbased_service_x_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 365
try:
    GSS_C_NT_HOSTBASED_SERVICE = pointer(__gss_c_nt_hostbased_service_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 378
try:
    GSS_C_NT_ANONYMOUS = pointer(__gss_c_nt_anonymous_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 391
try:
    GSS_C_NT_EXPORT_NAME = pointer(__gss_c_nt_export_name_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 398
try:
    GSS_SASL_DIGEST_MD5_MECHANISM = pointer(__gss_sasl_digest_md5_mechanism_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 405
try:
    GSS_C_INQ_SSPI_SESSION_KEY = pointer(__gss_c_inq_sspi_session_key_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 413
try:
    GSS_C_INQ_WIN2K_PAC_X = pointer(__gss_c_inq_win2k_pac_x_oid_desc)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 417
try:
    GSS_S_COMPLETE = 0
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 422
try:
    GSS_C_CALLING_ERROR_OFFSET = 24
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 423
try:
    GSS_C_ROUTINE_ERROR_OFFSET = 16
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 424
try:
    GSS_C_SUPPLEMENTARY_OFFSET = 0
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 425
try:
    GSS_C_CALLING_ERROR_MASK = 255
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 426
try:
    GSS_C_ROUTINE_ERROR_MASK = 255
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 427
try:
    GSS_C_SUPPLEMENTARY_MASK = 65535
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 435
def GSS_CALLING_ERROR(x):
    return (x & (GSS_C_CALLING_ERROR_MASK << GSS_C_CALLING_ERROR_OFFSET))

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 437
def GSS_ROUTINE_ERROR(x):
    return (x & (GSS_C_ROUTINE_ERROR_MASK << GSS_C_ROUTINE_ERROR_OFFSET))

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 439
def GSS_SUPPLEMENTARY_INFO(x):
    return (x & (GSS_C_SUPPLEMENTARY_MASK << GSS_C_SUPPLEMENTARY_OFFSET))

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 441
def GSS_ERROR(x):
    return (x & ((GSS_C_CALLING_ERROR_MASK << GSS_C_CALLING_ERROR_OFFSET) | (GSS_C_ROUTINE_ERROR_MASK << GSS_C_ROUTINE_ERROR_OFFSET)))

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 452
try:
    GSS_S_CALL_INACCESSIBLE_READ = (1 << GSS_C_CALLING_ERROR_OFFSET)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 454
try:
    GSS_S_CALL_INACCESSIBLE_WRITE = (2 << GSS_C_CALLING_ERROR_OFFSET)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 456
try:
    GSS_S_CALL_BAD_STRUCTURE = (3 << GSS_C_CALLING_ERROR_OFFSET)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 462
try:
    GSS_S_BAD_MECH = (1 << GSS_C_ROUTINE_ERROR_OFFSET)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 463
try:
    GSS_S_BAD_NAME = (2 << GSS_C_ROUTINE_ERROR_OFFSET)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 464
try:
    GSS_S_BAD_NAMETYPE = (3 << GSS_C_ROUTINE_ERROR_OFFSET)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 466
try:
    GSS_S_BAD_BINDINGS = (4 << GSS_C_ROUTINE_ERROR_OFFSET)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 467
try:
    GSS_S_BAD_STATUS = (5 << GSS_C_ROUTINE_ERROR_OFFSET)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 468
try:
    GSS_S_BAD_SIG = (6 << GSS_C_ROUTINE_ERROR_OFFSET)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 469
try:
    GSS_S_BAD_MIC = GSS_S_BAD_SIG
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 470
try:
    GSS_S_NO_CRED = (7 << GSS_C_ROUTINE_ERROR_OFFSET)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 471
try:
    GSS_S_NO_CONTEXT = (8 << GSS_C_ROUTINE_ERROR_OFFSET)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 472
try:
    GSS_S_DEFECTIVE_TOKEN = (9 << GSS_C_ROUTINE_ERROR_OFFSET)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 473
try:
    GSS_S_DEFECTIVE_CREDENTIAL = (10 << GSS_C_ROUTINE_ERROR_OFFSET)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 474
try:
    GSS_S_CREDENTIALS_EXPIRED = (11 << GSS_C_ROUTINE_ERROR_OFFSET)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 475
try:
    GSS_S_CONTEXT_EXPIRED = (12 << GSS_C_ROUTINE_ERROR_OFFSET)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 476
try:
    GSS_S_FAILURE = (13 << GSS_C_ROUTINE_ERROR_OFFSET)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 477
try:
    GSS_S_BAD_QOP = (14 << GSS_C_ROUTINE_ERROR_OFFSET)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 478
try:
    GSS_S_UNAUTHORIZED = (15 << GSS_C_ROUTINE_ERROR_OFFSET)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 479
try:
    GSS_S_UNAVAILABLE = (16 << GSS_C_ROUTINE_ERROR_OFFSET)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 480
try:
    GSS_S_DUPLICATE_ELEMENT = (17 << GSS_C_ROUTINE_ERROR_OFFSET)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 481
try:
    GSS_S_NAME_NOT_MN = (18 << GSS_C_ROUTINE_ERROR_OFFSET)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 482
try:
    GSS_S_BAD_MECH_ATTR = (19 << GSS_C_ROUTINE_ERROR_OFFSET)
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 487
try:
    GSS_S_CRED_UNAVAIL = GSS_S_FAILURE
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 492
try:
    GSS_S_CONTINUE_NEEDED = (1 << (GSS_C_SUPPLEMENTARY_OFFSET + 0))
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 493
try:
    GSS_S_DUPLICATE_TOKEN = (1 << (GSS_C_SUPPLEMENTARY_OFFSET + 1))
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 494
try:
    GSS_S_OLD_TOKEN = (1 << (GSS_C_SUPPLEMENTARY_OFFSET + 2))
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 495
try:
    GSS_S_UNSEQ_TOKEN = (1 << (GSS_C_SUPPLEMENTARY_OFFSET + 3))
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 496
try:
    GSS_S_GAP_TOKEN = (1 << (GSS_C_SUPPLEMENTARY_OFFSET + 4))
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 499
try:
    GSS_C_OPTION_MASK = 65535
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 500
try:
    GSS_C_CRED_NO_UI = 65536
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 506
try:
    GSS_C_PRF_KEY_FULL = 0
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 507
try:
    GSS_C_PRF_KEY_PARTIAL = 1
except:
    pass

# /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 510
try:
    GSS_C_ATTR_LOCAL_LOGIN_USER = pointer(__gss_c_attr_local_login_user)
except:
    pass

gss_name_t_desc_struct = struct_gss_name_t_desc_struct # /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 94

gss_ctx_id_t_desc_struct = struct_gss_ctx_id_t_desc_struct # /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 98

gss_OID_desc_struct = struct_gss_OID_desc_struct # /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 105

gss_OID_set_desc_struct = struct_gss_OID_set_desc_struct # /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 111

gss_cred_id_t_desc_struct = struct_gss_cred_id_t_desc_struct # /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 116

gss_buffer_desc_struct = struct_gss_buffer_desc_struct # /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 123

gss_channel_bindings_struct = struct_gss_channel_bindings_struct # /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 126

gss_buffer_set_desc_struct = struct_gss_buffer_set_desc_struct # /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 139

gss_iov_buffer_desc_struct = struct_gss_iov_buffer_desc_struct # /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 144

gss_auth_identity = struct_gss_auth_identity # /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 153

krb5_ccache_data = struct_krb5_ccache_data # /System/Library/Frameworks/GSS.framework/Headers/gssapi.h: 285

# No inserted files

