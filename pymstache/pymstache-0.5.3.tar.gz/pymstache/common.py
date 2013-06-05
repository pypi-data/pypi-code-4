# coding: utf-8

"""
Exposes functionality needed throughout the project.

"""
from pymongo import MongoClient
from sys import version_info

client = MongoClient(auto_start_request=True, w=1)

def _get_string_types():
    # TODO: come up with a better solution for this.  One of the issues here
    #   is that in Python 3 there is no common base class for unicode strings
    #   and byte strings, and 2to3 seems to convert all of "str", "unicode",
    #   and "basestring" to Python 3's "str".
    if version_info < (3, ):
         return basestring
    # The latter evaluates to "bytes" in Python 3 -- even after conversion by 2to3.
    return (unicode, type(u"a".encode('utf-8')))


_STRING_TYPES = _get_string_types()


def is_string(obj):
    """
    Return whether the given object is a byte string or unicode string.

    This function is provided for compatibility with both Python 2 and 3
    when using 2to3.

    """
    return isinstance(obj, _STRING_TYPES)


# This function was designed to be portable across Python versions -- both
# with older versions and with Python 3 after applying 2to3.
def read(path, db='__main', collection='template'):
    """
    Return the contents of a text file as a byte string.

    """
    # We avoid use of the with keyword for Python 2.4 support.
    request = client.start_request()
    try:
        return client[db][collection].find_one({'path': path}).get("content")
    except:
        raise TemplateNotFoundError()
    finally:
        request.end()

class MissingTags(object):

    """Contains the valid values for Renderer.missing_tags."""

    ignore = 'ignore'
    strict = 'strict'


class PystacheError(Exception):
    """Base class for Pystache exceptions."""
    pass


class TemplateNotFoundError(PystacheError):
    """An exception raised when a template is not found."""
    pass
