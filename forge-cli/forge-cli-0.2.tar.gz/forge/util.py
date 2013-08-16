#!/usr/bin/env python
"""
forge.util
~~~~~

:copyright: (c) 2010-2013 by Luis Morales
:license: BSD, see LICENSE for more details.
"""

import os
import sys
import inspect


def check_root():
    """
    Check if we have root permissions before starting
    """
    if not 'SUDO_UID' in os.environ.keys():
        print "This program requires super user priv."
        sys.exit(1)
    elif os.geteuid() != 0:
        print 'This program requires super user priv.'
        sys.exit(1)


def load_class_from_name(fqcn):
    # Break apart fqcn to get module and classname
    paths = fqcn.split('.')
    modulename = '.'.join(paths[:-1])
    classname = paths[-1]
    # Import the module
    __import__(modulename, globals(), locals(), ['*'])
    # Get the class
    cls = getattr(sys.modules[modulename], classname)
    # Check cls
    if not inspect.isclass(cls):
        raise TypeError("%s is not a class" % fqcn)
    # Return class
    return cls
