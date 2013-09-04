# Copyright (C) 2012-2013 Peter Hatina <phatina@redhat.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

import os
import sys
import subprocess
from site import _Helper

from LMIUtil import lmi_script_name

class LMIHelper(_Helper):
    """
    LMI Helper class, which overrides python help.
    """
    def __repr__(self):
        """
        Returns a pretty string for the object.
        """
        return "Type help() to see man page for %s, " \
            "or help(object) for help about object." % lmi_script_name()

    def __call__(self, *args, **kwargs):
        """
        Executes either man page for LMIShell or prints pydoc help for an object.
        """
        if not args and not kwargs:
            try:
                # Python 3+
                from subprocess import DEVNULL as devnull
                devnull_close = lambda: None
            except ImportError:
                devnull = open(os.devnull, "wb")
                devnull_close = lambda: devnull.close()
            rcode = subprocess.call(["man", lmi_script_name()], stderr=devnull)
            devnull_close()
            if rcode > 0:
                sys.stderr.write("Man page for %s can not be found, " % lmi_script_name())
                sys.stderr.write("refer to Wiki page instead.\n\n")
                sys.stderr.write("Available at: https://fedorahosted.org/openlmi/wiki/shell\n" )
        else:
            import pydoc
            return pydoc.help(*args, **kwargs)
