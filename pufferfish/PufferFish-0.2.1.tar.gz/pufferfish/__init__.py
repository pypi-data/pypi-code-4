#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (c) 2011 Giacomo Bagnoli <g.bagnoli@asidev.com>

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

"""
Pufferfish provides a FileSystemEntity class that can be used for those mapped
objects that need to keep files on the filesystem (i.e. to be served by the
webserver directly). It uses SQLAlchemy 0.7 events to handle rollback and
commits on deleted/updated and new objects ( a new file will be removed on
rollbacks, while a delete file will be removed only after a successful commit,
etc).
"""

try:
    from fsentity import FileSystemEntity
except ImportError:  # pragma: nocover
    pass

__all__ = ['FileSystemEntity',
           '__version__', 'version_string',
           'version_string', '__author__',
           '__copyright__', '__maintainer__',
           '__email__', '__status__']

__version__ = (0, 2, 1, "final", 0)
__author__ = "Giacomo Bagnoli"
__copyright__ = 'Copyright (C) 2010, Asidev s.r.l.'
__maintainer__ = "Giacomo Bagnoli"
__email__ = "info@asidev.com"
