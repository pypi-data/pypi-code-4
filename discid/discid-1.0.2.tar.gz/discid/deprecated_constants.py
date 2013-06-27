# Copyright (C) 2013  Johannes Dewender
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Please submit bug reports to GitHub:
# https://github.com/JonnyJD/python-discid/issues
"""Deprecated functions and classes
"""

import sys
import types
import warnings
from warnings import warn_explicit, warn

from discid.libdiscid import get_default_device


#class _Constants(types.ModuleType):
class _Constants(object):
    def get_default_device(self):
        #warnings.warn("DEFAULT_DEVICE is deprecated.\n"
        #     "Use get_default_device() instead",
        #     DeprecationWarning)
        return get_default_device()
        #return "blub"
    DEFAULT_DEVICE = property(get_default_device)

#print(sys.modules[__name__])
sys.modules[__name__] = _Constants()
sys.modules["discid.deprecated_const"] = _Constants()
