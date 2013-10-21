#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fsentity import FileSystemEntity
from session import add_session_hooks
from elixir import using_options

__all__ = [ 'File' ]
__session__ = None

class File(FileSystemEntity):
    """ Simple class that can be used as an elixir Entity
        that keeps the file on disk.
        This class must be configured prior to use

        >>> from pufferfish import File
        >>> File.set_paths(base="/tmp/testme", private="/tmp")
        ... 
    """
    add_session_hooks()
    using_options(tablename="file")
