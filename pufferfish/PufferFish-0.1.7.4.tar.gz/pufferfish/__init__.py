#!/usr/bin/env python
"""
PufferFish provides an SQLAlchemy session that provides hooks for various
events link commits and rollbacks.
It provides a FileSystemEntity class that can be used as a base Elixir class
for those entities that need to keep files on the filesystem (i.e. to be
served by the webserver directly). It use session hooks to handle rollback and
commits on deleted/updated and new objects ( a new file will be removed on
rollbacks, while a delete file will be removed only after a successful commit,
etc).
"""

from fsentity import FileSystemEntity
from session import HookableSessionExtension, add_session_hooks, HookableSession

version = (0,1,7)
__version__ = "%d.%d.%d" % version
version_string = "PufferFish version %s " % __version__

__author__ = "Giacomo Bagnoli"
__copyright__ = 'Copyright (C) 2010, Asidev s.r.l.'
__maintainer__ = "Giacomo Bagnoli"
__email__ = "info@asidev.com"
__status__ = "Alpha"
