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

# Base class for classes, that are used for tab-completion.
# Used due to deprecated methods since python 2.2.

class LMIBaseObject(object):
    """
    Base class for all LMI classes. It is useful for rlcompleter
    module.
    """
    # deprecated
    def __methods__(self):
        return []

    # deprecated
    def __members__(self):
        return []

    def __call__(self):
        pass

class LMIWrapperBaseObject(LMIBaseObject):
    """
    Base class for all LMI wrapper classes, such as LMINamespace, LMIClass,
    LMIInstanceName, LMIInstance, LMIMethod.
    """
    def __init__(self, conn):
        """
        Constructs LMIWrapperBaseObject instance.

        Arguments:
            conn -- LMIConnection object
        """
        super(LMIWrapperBaseObject, self).__init__()
        self._conn = conn

    @property
    def connection(self):
        """
        Property returning LMIConnection object.
        """
        return self._conn
