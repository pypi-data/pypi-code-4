#!/usr/bin/env python

"""
Wrapper for Veracity's command-line interface.
"""

import os
from collections import defaultdict

from veracity import settings

try:  # pragma: no cover, installation
    if os.name == 'nt':
        import pbs  # pylint: disable=F0401,W0611
        ErrorReturnCode = pbs.ErrorReturnCode  # pylint: disable=C0103
        if not os.path.isfile(settings.VV_PATH_WINDOWS):
            raise ImportError
        vv = pbs.Command(settings.VV_PATH_WINDOWS)  # pylint: disable=C0103
    else:
        from sh import ErrorReturnCode  # pylint: disable=F0401,W0611
        from sh import vv  # pylint: disable=F0401,E0611
except ImportError:  # pragma: no cover, installation
    VERSION = ''
else:
    VERSION = str(vv.version()).strip()
if not VERSION:  # pragma : no cover, no automated test
    raise EnvironmentError("Veracity 2.5 is not installed")
if not VERSION.startswith('2.5'):  # pragma : no cover, no automated test
    raise EnvironmentError("only Veracity 2.5 is supported, "
                           "current: {0}".format(VERSION))


class VeracityException(Exception):
    """Exception for Veracity errors."""
    pass


def repos():
    """Return a list of local repository names.
    """
    return run('repos').splitlines()


def version():
    """Return the version string.
    """
    return VERSION


def run(*args, **kwargs):
    """Run a Veracity command with the given arguments.
    @raise VeracityException: when Veracity returns an error
    """
    command = vv.bake(*args, **kwargs)
    # TODO: this isn't working in Python 3
    # logging.debug("$ {0}".format(command))
    try:
        result = command()
    except ErrorReturnCode as erc:
        msg = ("\n\nIN: {0}"
               "\n\nRAN: {1}"
               "\n\nOUTPUT:{2}\n").format(os.getcwd(),
                                          erc.full_cmd,
                                          erc.stderr.strip())
        raise VeracityException(msg)
    else:
        # TODO: apparently pbs returns str not byte
        if os.name == 'nt':
            return result.stdout.strip()
        else:
            return result.stdout.decode('utf-8').strip()


def parse(output, style=None):  # pylint: disable=R0912
    """Yield parsed lines of Veracity output.
    """
    changeset = defaultdict(list)

    for line in output.splitlines():

        if not style:
            yield line

        elif style == 'indented':
            ##################################################################
            # label
            #     <ignore>
            ##################################################################
            if line and not line.startswith('   '):
                yield line

        elif style == 'tags':
            ##################################################################
            #                label:     local:revision
            ##################################################################
            if line:
                yield tuple(part.strip() for part in line.split(':', 2))

        elif style == 'stamps':
            ##################################################################
            # label:       count
            # label: count
            ##################################################################
            if line:
                yield tuple(part.strip() for part in line.split(':', 1))

        elif style == 'files':
            ##################################################################
            #        change:  + @/path
            #        change:    @/path
            ##################################################################
            if '@/' in line:
                _prefix, path = line.split('@/')
                change = _prefix.split(':')[0].strip()
                yield change, path

        elif style == 'changesets':
            ##################################################################
            #        revision:  14:0c340fca55d2ef45e27ef8c906f82c6b1aadd016
            #          branch:  build_tracking
            #             who:  jacebrowning@gmail.com
            #            when:  2013/03/07 01:51:36.713 +0000
            #         comment:  added possible CLI for build tracking
            #          parent:  13:bd0cd7bb50a18b7d4d156db3c106f572ff3ffb04
            #
            #        revision:  18:518a7e0ed1fe30112cbad9a462115de863f9e2cf
            #          branch:  master
            #             who:  jacebrowning@gmail.com
            #            when:  2013/06/27 13:57:42.942 +0100
            #         comment:  fixed a test failure in Windows
            #          parent:  17:c7ee91e77c61a9b7b1ed85ea7356c57b57a05ee0
            ##################################################################
            if line.strip() and not line.startswith("Parents"):
                key, value = line.split(':  ')
                changeset[key.strip()].append(value)
            elif changeset:
                yield changeset
                changeset = defaultdict(list)

        else:
            raise ValueError("unknown format: {0}".format(format))

    if changeset:
        yield changeset
