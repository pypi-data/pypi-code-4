# -*- coding: utf-8 -*-
VERSION = (0, 8, 0, 'b', 4)

def get_version(): # pragma: no cover
    version = '%s.%s' % (VERSION[0], VERSION[1])
    if VERSION[2]:
        version = '%s.%s' % (version, VERSION[2])
    else:
        if VERSION[3] != 'final':
            version = '%s.%s%s' % (version, VERSION[3], VERSION[4])
    return version
