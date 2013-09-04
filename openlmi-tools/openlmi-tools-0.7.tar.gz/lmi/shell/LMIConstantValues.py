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

import abc
import sys

from LMIBaseObject import LMIBaseObject
from LMIUtil import lmi_cast_to_lmi

class LMIConstantValues(LMIBaseObject):
    """
    Abstract class for constant value objects.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, cim_obj, cast_type):
        """
        Constructs a object.

        Arguments:
            cim_obj -- this object is either of type CIMParameter, CIMProperty or
                CIMMethod. Construction of this object requires to have a member "_cast_type"
                to properly cast CIM object. When constructing defived objects, make sure,
                that the mentioned member is present before calling this constructor.
            cast_type -- parameter/property cast type
        """
        # Keys can contain various undesirable characters, such as python
        # operators, etc. So we drop them.
        keys = map(lambda v: "".join(c for c in v if c.isalnum()),
            cim_obj.qualifiers["Values"].value)
        values = cim_obj.qualifiers["ValueMap"].value
        self._value_map = {}
        self._value_map_inv = {}
        self._cast_type = cast_type
        # Fill two dictionaries for bidirectional access to constant values.
        for i in range(0, len(keys)):
            try:
                key = keys[i]
                val = lmi_cast_to_lmi(self._cast_type, values[i])
                self._value_map[key] = val
                self._value_map_inv[val] = key
            except ValueError, e:
                # Can not cast such value as interval. Can be found in
                # DMTFReserved, VendorReserved values.
                pass

    def __repr__(self):
        """
        Returns a string of all constant names with corresponding value.
        """
        result = ""
        for (k, v) in self._value_map.iteritems():
            result += "%s = %s\n" % (k, v)
        return result[:-1]

    def __getattr__(self, name):
        """
        Returns either a member of the class, or a constant value.

        Simplifies the code and constant value can be retrieved by
        object.constant_value.

        Arguments:
            name -- string containing a member to retrieve
        """
        if name in self.__dict__:
            return self.__dict__[name]
        if name in self._value_map:
            return self._value_map[name]
        raise AttributeError(name)

    def print_values(self):
        """
        Prints all available constant names.
        """
        for k in self._value_map.keys():
            sys.stdout.write("%s\n" % k)

    def values_dict(self):
        """
        Returns a dictionary of constants' names and values.
        """
        return self._value_map

    def values(self):
        """
        Returns a list of all available constant values.
        """
        return self._value_map.keys()

    def value(self, value_name):
        """
        Returns a constant value.

        Arguments:
            value_name -- string containing a constant name
        """
        return getattr(self, value_name)

    def value_name(self, value):
        """
        Returns string representing constant value.

        Arguments:
            value -- numeric constant value
        """
        return self._value_map_inv[value]

class LMIConstantValuesParamProp(LMIConstantValues):
    """
    Derived class used for constant values of CIMProperty and CIMParameter.
    """
    def __init__(self, cim_property):
        """
        Constructs a object.

        Arguments:
            cim_property -- CIMProperty or CIMParameter object. Both objects have
                necessary member "type" which is needed for proper casting.
        """
        super(LMIConstantValuesParamProp, self).__init__(cim_property, cim_property.type)

class LMIConstantValuesMethodReturnType(LMIConstantValues):
    """
    Derived class used for constant values of CIMMethod.
    """
    def __init__(self, cim_method):
        """
        Constructs a object.

        Arguments:
            cim_method -- CIMMethod object
        """
        super(LMIConstantValuesMethodReturnType, self).__init__(cim_method, cim_method.return_type)
