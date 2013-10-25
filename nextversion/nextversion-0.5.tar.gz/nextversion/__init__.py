# -*- coding: utf-8 -*-
"""
    nextversion
    ~~~~~~~~~~~

    Increments module verision numbers.::

        from nextversion import nextversion
        nextversion('1.0a2')    # => '1.0a3'
        nextversion('v1.0a2')   # => '1.0a3'  (normalized to compatible version with PEP 386)
        nextversion('foo.0.3')  # => None     (impossible to normalize)

    If original version number does not match `PEP 386 <//www.python.org/dev/peps/pep-0386/>`_ ,

    1. Next version compatible with `PEP 386 <//www.python.org/dev/peps/pep-0386/>`_ is returned if possible,
    2. If impossible, `None` is returned.
"""
__version__   = '0.5'
__author__    = 'Sho Nakatani'
__email__     = 'lay.sakura@gmail.com'
__copyright__ = 'Copyright 2013, Sho Nakatani'


import nextversion.core as core


def nextversion(current_version):
    """Returns incremented module version number.

    :param current_version: version string to increment
    :returns:               Next version string (PEP 386 compatible) if possible.
                            If impossible (since `current_version` is too far from PEP 386),
                            `None` is returned.
    """
    return core.nextversion(current_version)
