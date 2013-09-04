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

import sys

from LMIBaseObject import LMIWrapperBaseObject
from LMIUtil import lmi_wrap_cim_instance

class LMIInstanceName(LMIWrapperBaseObject):
    """
    LMI wrapper class representing CIMInstanceName.
    """
    def __init__(self, conn, cim_instance_name):
        """
        Constructs a LMIInstanceName object.

        Arguments:
            conn -- LMIConnection object
            cim_instance_name -- CIMInstanceName object
        """
        super(LMIInstanceName, self).__init__(conn)
        self._cim_instance_name = cim_instance_name

    def __getattr__(self, name):
        """
        Returns either a class member, or a key property value.

        Simplifies the code. Key properties values can be retrieved by
        object.key_property.

        Arguments:
            name -- string containing the class member, or the key property name
        """
        if name in self.__dict__:
            return self.__dict__[name]
        key_props = self.key_properties()
        if key_props and name in key_props:
            return self._cim_instance_name[name]
        raise AttributeError(name)

    def __repr__(self):
        """
        Returns a pretty string for the object.
        """
        return "%s(...)" % self.__class__.__name__

    def to_instance(self):
        """
        Creates a new LMIInstance object from LMIInstanceName by calling a
        GetInstance(). Returns a LMIInstance object if the object was retrieved
        successfuly; otherwise None.
        """
        (cim_instance, _, errorstr) = self._conn._client._get_instance(
            self._cim_instance_name, LocalOnly=False)
        if not cim_instance:
            return None
        return lmi_wrap_cim_instance(self._conn, cim_instance,
            self._cim_instance_name.classname,
            self._cim_instance_name.namespace
        )

    def key_properties(self):
        """
        Returns a list of strings of key properties.
        """
        return self._cim_instance_name.keys()

    def print_key_properties(self):
        """
        Prints out the list of key properties.
        """
        for name in self._cim_instance_name.keys():
            sys.stdout.write("%s\n" % name)

    def key_properties_dict(self):
        """
        Returns a dictionary with key properties and corresponding values.
        """
        return self._cim_instance_name.keybindings.copy()

    def key_property_value(self, prop_name):
        """
        Returns a value of the specified key property.

        Arguments:
            prop_name -- string containing the key property name
        """
        return getattr(self, prop_name)

    @property
    def classname(self):
        """
        Property returning a string of the class name.
        """
        return self._cim_instance_name.classname

    @property
    def namespace(self):
        """
        Property returning a string of the namespace name.
        """
        return self._cim_instance_name.namespace

    @property
    def path(self):
        """
        Property returning a string of CIMInstance path.
        """
        return self._cim_instance_name
