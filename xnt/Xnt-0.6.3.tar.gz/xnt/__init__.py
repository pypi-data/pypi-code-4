#!/usr/bin/env python
"""Main xnt module

Contains definition for version (referenced from version module), license,
target decorator, and imports task methods from tasks module
"""

#   Xnt -- A Wrapper Build Tool
#   Copyright (C) 2013  Kenny Ballou

#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.

#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.

#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

import xnt.version
__version__ = "Xnt " + xnt.version.__version__
__license__ = """
   Xnt -- A Wrapper Build Tool
   Copyright (C) 2012  Kenny Ballou

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

VERBOSE = False

from xnt.tasks import cp
from xnt.tasks import mv
from xnt.tasks import mkdir
from xnt.tasks import rm
from xnt.tasks import create_zip
from xnt.tasks import log
from xnt.tasks import xntcall
from xnt.tasks import call
from xnt.tasks import setup
from xnt.tasks import which
from xnt.tasks import in_path

def target(*args, **kwargs):
    """Decorator function for marking a method in
       build file as a "target" method, or a method meant
       to be invoked from Xnt
    """
    def w_target(target_fn):
        """target wrapping function"""
        has_run = [False,]
        def wrap():
            """Inner wrapper function for decorator"""
            if not has_run[0] or kwargs.get('always_run', False):
                has_run[0] = True
                print(target_fn.__name__ + ":")
                return target_fn()
            return None
        wrap.decorator = "target"
        wrap.__doc__ = target_fn.__doc__
        return wrap
    if len(args) == 1 and callable(args[0]):
        return w_target(args[0])
    return w_target
