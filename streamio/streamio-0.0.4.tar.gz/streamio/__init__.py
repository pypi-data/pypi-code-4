# Package:  streamio
# Date:     18th December 2012
# Author:   James Mills, j dot mills at griffith dot edu dot au

"""streamio - reading, writing and sorting large files.

streamio is a simple library of functions designed to read, write and sort large files using iterators so that the operations will successfully complete
on systems with limited RAM.

:copyright: CopyRight (C) 2013 by James Mills
"""

__author__ = "James Mills, j dot mills at griffith dot edu dot au"
__date__ = "21st November 2013"

from .version import version as __version__  # noqa

from .stat import minmax  # noqa
from .sort import merge, mergesort  # noqa
from .stream import stream, csvstream, jsonstream, csvdictstream, compress  # noqa

__all__ = ("minmax", "merge", "mergesort", "stream", "csvstream", "jsonstream", "csvdictstream", "compress",)
