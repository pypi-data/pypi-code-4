#!/usr/bin/env python

"""
Package for veracity.
"""

from pkg_resources import get_distribution, DistributionNotFound

__project__ = 'python-veracity'
__version__ = None  # required for initial installation

TRACKING = 'vv-tracking'
POLLER = 'vv-poller'
BUILDER = 'vv-builder'

try:
    __version__ = get_distribution(__project__).version  # pylint: disable=E1103
except DistributionNotFound:  # pragma: no cover, installation
    VERSION = __project__ + '-' + '(local)'
else:
    VERSION = __project__ + '-' + __version__

try:
    from veracity.vv import VeracityException
    from veracity.vv import repos, run as run_vv
    from veracity.objects import Repository, WorkingCopy
    from veracity.objects import Item, Changeset, Branch, Stamp, Tag, User
    from veracity.objects import BuildRequest
except (ImportError, EnvironmentError) as error:  # pragma: no cover, installation
    print(error)
