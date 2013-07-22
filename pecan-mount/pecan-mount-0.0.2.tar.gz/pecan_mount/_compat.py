"""Compatibility code for various versions of Python.

In particular, Python 2 uses str and '' for byte strings, while Python 3
uses str and '' for unicode strings. We will call each of these the 'native
string' type for each version. Because of this major difference, this module
provides new 'bytestr', 'unicodestr', and 'nativestr' attributes, as well as
two functions: 'ntob', which translates native strings (of type 'str') into
byte strings regardless of Python version, and 'native_to_unicode', which translates native
strings to unicode strings. This also provides a 'BytesIO' name for dealing
specifically with bytes, and a 'StringIO' name for dealing with native strings.
It also provides a 'base64_decode' function with native strings as input and
output.
"""
import os
import re
import sys
import threading

if sys.version_info >= (3, 0):
    py3k = True
    bytestr = bytes
    unicodestr = str
    nativestr = unicodestr
    basestring = (bytes, str)
    def ntob(n, encoding='ISO-8859-1'):
        """Return the given native string as a byte string in the given encoding."""
        assert_native(n)
        # In Python 3, the native string type is unicode
        return n.encode(encoding)
    def native_to_unicode(n, encoding='ISO-8859-1'):
        """Return the given native string as a unicode string with the given encoding."""
        assert_native(n)
        # In Python 3, the native string type is unicode
        return n
    def tonative(n, encoding='ISO-8859-1'):
        """Return the given string as a native string in the given encoding."""
        # In Python 3, the native string type is unicode
        if isinstance(n, bytes):
            return n.decode(encoding)
        return n
    # type("")
    from io import StringIO
    # bytes:
    from io import BytesIO as BytesIO
else:
    # Python 2
    py3k = False
    bytestr = str
    unicodestr = unicode
    nativestr = bytestr
    basestring = basestring
    def ntob(n, encoding='ISO-8859-1'):
        """Return the given native string as a byte string in the given encoding."""
        assert_native(n)
        # In Python 2, the native string type is bytes. Assume it's already
        # in the given encoding, which for ISO-8859-1 is almost always what
        # was intended.
        return n
    def native_to_unicode(n, encoding='ISO-8859-1'):
        """Return the given native string as a unicode string with the given encoding."""
        assert_native(n)
        # In Python 2, the native string type is bytes.
        # First, check for the special encoding 'escape'. The test suite uses this
        # to signal that it wants to pass a string with embedded \uXXXX escapes,
        # but without having to prefix it with u'' for Python 2, but no prefix
        # for Python 3.
        if encoding == 'escape':
            return unicode(
                re.sub(r'\\u([0-9a-zA-Z]{4})',
                       lambda m: unichr(int(m.group(1), 16)),
                       n.decode('ISO-8859-1')))
        # Assume it's already in the given encoding, which for ISO-8859-1 is almost
        # always what was intended.
        return n.decode(encoding)
    def tonative(n, encoding='ISO-8859-1'):
        """Return the given string as a native string in the given encoding."""
        # In Python 2, the native string type is bytes.
        if isinstance(n, unicode):
            return n.encode(encoding)
        return n
    try:
        # type("")
        from cStringIO import StringIO
    except ImportError:
        # type("")
        from StringIO import StringIO
    # bytes:
    BytesIO = StringIO

def assert_native(n):
    if not isinstance(n, nativestr):
        raise TypeError("n must be a native str (got %s)" % type(n).__name__)


