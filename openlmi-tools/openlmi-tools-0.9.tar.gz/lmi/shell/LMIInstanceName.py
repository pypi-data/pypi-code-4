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
import pywbem

from LMIBaseObject import LMIWrapperBaseObject
from LMIUtil import lmi_wrap_cim_instance
from LMIUtil import lmi_wrap_cim_instance_name

class LMIInstanceName(LMIWrapperBaseObject):
    """
    LMI wrapper class representing :py:class:`CIMInstanceName`.

    :param LMIConnection conn: connection object
    :param CIMInstanceName cim_instance_name: wrapped object
    """
    def __init__(self, conn, cim_instance_name):
        super(LMIInstanceName, self).__init__(conn)
        if isinstance(cim_instance_name, LMIInstanceName):
            cim_instance_name = cim_instance_name.wrapped_object
        self._cim_instance_name = cim_instance_name

    def __contains__(self, key):
        """
        :param string key: key name, which will be tested for presence in keybindings
        :returns: True, if the specified key is present in keybindings, False otherwise
        """
        return key in self._cim_instance_name

    def __getattr__(self, name):
        """
        Simplifies the code. Key properties values can be retrieved by
        :samp:`object.key_property`.

        :param string name: class member or key property name
        :returns: class member or key property
        """
        if name in self.__dict__:
            return self.__dict__[name]
        key_props = self.key_properties()
        if key_props and name in key_props:
            member = self._cim_instance_name[name]
            if isinstance(member, pywbem.CIMInstanceName):
                member = lmi_wrap_cim_instance_name(self._conn, member)
            return member
        raise AttributeError(name)

    def __str__(self):
        """
        :returns: string of serialized object
        """
        return "%s(classname=\"%s\", %s)" % ( \
            self.__class__.__name__, \
            self.classname, \
            str(self._cim_instance_name) \
        )

    def __repr__(self):
        """
        :returns: pretty string for the object
        """
        return "%s(classname=\"%s\"...)" % ( \
            self.__class__.__name__, \
            self.classname \
        )

    def copy(self):
        """
        :returns: copy of itself
        """
        return lmi_wrap_cim_instance_name(
                self._conn, self._cim_instance_name.copy())

    def to_instance(self):
        """
        Creates a new :py:class:`LMIInstance` object from :py:class:`LMIInstanceName`.

        :returns: :py:class:`LMIInstance` object if the object was retrieved successfully;
            None otherwise.

        **Usage:** :ref:`instance_names_conversion`.
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
        :returns: list of strings of key properties

        **Usage:** :ref:`instance_names_key_properties`.
        """
        return self._cim_instance_name.keys()

    def print_key_properties(self):
        """
        Prints out the list of key properties.

        **Usage:** :ref:`instance_names_key_properties`.
        """
        for name in self._cim_instance_name.keys():
            sys.stdout.write("%s\n" % name)

    def key_properties_dict(self):
        """
        :returns: dictionary with key properties and corresponding values
        """
        return self._cim_instance_name.keybindings.copy()

    def key_property_value(self, prop_name):
        """
        :param string prop_name: key property name
        :returns: key property value
        """
        return getattr(self, prop_name)

    @property
    def classname(self):
        """
        :returns: class name
        :rtype: string
        """
        return self._cim_instance_name.classname

    @property
    def namespace(self):
        """
        :returns: namespace name
        :rtype: string
        """
        return self._cim_instance_name.namespace

    @property
    def hostname(self):
        """
        :returns: host name
        :rtype: string
        """
        return self._cim_instance_name.host

    @property
    def wrapped_object(self):
        """
        :returns: wrapped :py:class:`CIMInstanceName` object
        """
        return self._cim_instance_name
