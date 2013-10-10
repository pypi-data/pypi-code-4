"""
Extract useful information from a VCARD file.


Copyright (c) 2013 Jeroen F.J. Laros <jlaros@fixedpoint.nl>

Licensed under the MIT license, see the LICENSE file.
"""

__version_info__ = ('0', '3', '0')


__version__ = '.'.join(__version_info__)
__author__ = 'Jeroen F.J. Laros'
__contact__ = 'jlaros@fixedpoint.nl'
__homepage__ = 'http://www.fixedpoint.nl'

usage = __doc__.split("\n\n\n")

def docSplit(func):
    return func.__doc__.split("\n\n")[0]

def version(name):
    return "%s version %s\n\nAuthor   : %s <%s>\nHomepage : %s" % (name,
        __version__, __author__, __contact__, __homepage__)
