# coding: utf-8
"""pypel package, simple receipts management tool.

THIS SOFTWARE IS UNDER BSD LICENSE.
Copyright (c) 2012-2013 Daniele Tricoli <eriol@mornie.org>

Read LICENSE for more informations.
"""

__version_info__ = (0, 2, 0, 'final', 0)


def get_version():
    """Returns project version in a human readable form."""
    version_numbers = 2 if __version_info__[2] == 0 else 3
    version = '.'.join(str(x) for x in __version_info__[:version_numbers])

    assert __version_info__[3] in ('alpha', 'beta', 'candidate', 'final')

    release = ''

    if __version_info__[3] != 'final':
        release = __version_info__[3][0] + str(__version_info__[4])

    return version + release

__version__ = get_version()
