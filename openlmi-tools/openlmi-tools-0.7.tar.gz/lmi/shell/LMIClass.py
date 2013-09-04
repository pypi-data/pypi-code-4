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
from LMIBaseClient import LMIBaseClient
from LMIFormatter import LMIXmlFormatter
from LMIConstantValues import LMIConstantValuesParamProp

from LMIExceptions import LMIUnknownPropertyError

from LMIDecorators import lmi_class_fetch_lazy
from LMIDecorators import lmi_return_val_if_fail
from LMIDecorators import lmi_return_if_fail

from LMIUtil import lmi_cast_to_cim
from LMIUtil import lmi_raise_or_dump_exception
from LMIUtil import lmi_wrap_cim_instance
from LMIUtil import lmi_wrap_cim_instance_name

class LMIClass(LMIWrapperBaseObject):
    """
    LMI wrapper class representing CIMClass.
    """
    def __init__(self, conn, namespace, classname):
        """
        Constructs a LMIClass object.

        Arguments:
            conn -- LMIConnection object
            namespace -- LMINamespace object used for CIMInstances retrieval
            classname -- string containing CIM class name
        """
        # We use __dict__ to avoid recursion potentially caused by
        # combo __setattr__ and __getattr__
        self.__dict__["_namespace"] = namespace
        self.__dict__["_cim_class"] = None
        self.__dict__["_cim_classname"] = classname
        super(LMIClass, self).__init__(conn)

    def __repr__(self):
        """
        Returns a pretty string for the object.
        """
        return "%s(classname='%s', ...)" % (self.__class__.__name__, self.classname)

    @lmi_class_fetch_lazy
    def __getattr__(self, name):
        """
        Returns either a class member, or a constant value.

        Simplifies the code and constant value can be retrieved by
        object.constant_value.

        Arguments:
            name -- string containing either object member or constant values member.
        """
        if name in self.__dict__:
            return self.__dict__[name]
        if name.endswith("Values"):
            property_name = name[:-6]
            return LMIConstantValuesParamProp(self._cim_class.properties[property_name])
        raise AttributeError(name)

    @lmi_class_fetch_lazy
    @lmi_return_val_if_fail(lambda obj: obj._namespace, None)
    def create_instance(self, properties=None, qualifiers=None, property_list=None):
        """
        Creates a new CIMInstance at the server side and returns LMIReturnValue
        containing LMIInstance as a result.

        Arguments:
            properties -- doctionary containing initial properties with corresponding values
            qualifiers -- dictionary with initial qualifiers
            property_list -- pywbem.CIMInstance.property_list
        """
        # No need to copy dictionaries to avoid the variable mixup, the copying is done in
        # LMIBaseClient._create_instance(), we just pass what we get.
        properties = properties if not properties is None else {}
        qualifiers = qualifiers if not qualifiers is None else {}
        self_properties = self._cim_class.properties
        for (key, value) in properties.iteritems():
            if not key in self._cim_class.properties:
                errorstr = "No such instance property '%s'" % key
                lmi_raise_or_dump_exception(LMIUnknownPropertyError(errorstr))
                return None
            t = self._cim_class.properties[key].type
            properties[key] = lmi_cast_to_cim(t, value)
        (cim_instance, rparams, errorstr) = self._conn._client._create_instance(self.classname,
            self.namespace, properties, qualifiers, property_list)
        if not cim_instance:
            return None
        return lmi_wrap_cim_instance(self._conn, cim_instance, cim_instance.classname,
            cim_instance.path.namespace)

    @lmi_class_fetch_lazy
    @lmi_return_if_fail(lambda obj: obj._namespace)
    def doc(self):
        """
        Prints out pretty verbose message with documentation for the class. If the LMIShell
        is run in a interactive mode, the output will be redirected to a pager set by
        environment variable PAGER. If there is not PAGER set, less or more will be used
        as a fallback.
        """
        LMIXmlFormatter(self._cim_class.tocimxml()).fancy_format(self._conn._client.interactive)

    def fetch(self):
        """
        Calls GetClass() method. Manually fetches a CIMClass.
        """
        if self._cim_class or not self._namespace:
            # We already have CIMClass, or we do not know the namespace, from which
            # the class should be fetched.
            return
        (self._cim_class, _, _) = self._conn._client._get_class(self._cim_classname,
            self._namespace.name, LocalOnly=False)
        # Store the constant values as a list. This can consume some time, if computed on demand.
        self._valuemap_properties_list = [k for (k, v) in self._cim_class.properties.iteritems() \
            if "ValueMap" in v.qualifiers]

    # NOTE: usage with Key=something, Value=something is deprecated
    # NOTE: inst_filter is either None or dict
    @lmi_return_val_if_fail(lambda obj: obj._namespace, [])
    def instance_names(self, inst_filter=None, **kwargs):
        """
        Returns a LMIReturnValue containing a list of LMIInstanceNames.

        Arguments:
            inst_filter -- dictionary containing filter values. The key corresponds to the
                primary key of the CIMInstanceName; value contains the filtering value.

        Keyword Arguments (deprecated):
            Key, key -- filtering key, see above
            Value, value -- filtering value, see above
        """
        (inst_name_list, _, errorstr) = self._conn._client._get_instance_names(
            self._cim_classname,  self._namespace.name, inst_filter, **kwargs)
        if not inst_name_list:
            return []
        return map(lambda inst_name: lmi_wrap_cim_instance_name(self._conn, inst_name), inst_name_list)

    def new_instance_name(self, keybindings):
        """
        Create new LMIInstanceName object by passing all the keys/values of the object.
        Returns LMIInstanceName object with specified keybindings.

        Arguments:
            keybindigs -- dictionary containing primary keys of instance name with
                corresponding values
        """
        cim_inst_name = pywbem.CIMInstanceName(self.classname, keybindings,
            namespace=self.namespace)
        return lmi_wrap_cim_instance_name(self._conn, cim_inst_name)

    # NOTE: usage with Key=something, Value=something is deprecated
    # NOTE: inst_filter is either None or dict
    def first_instance_name(self, inst_filter=None, **kwargs):
        """
        Returns the first LMIInstanceName of the corresponding class.

        Arguments:
            inst_filter -- dictionary containing filter values. The key corresponds to the
                primary key of CIMInstanceName; value contains the filtering value.

        Keyword Arguments (deprecated):
            Key, key -- filtering key, see above
            Value, value -- filtering value, see above
        """
        inst_name_list = self.instance_names(inst_filter, **kwargs)
        if not inst_name_list:
            return None
        return inst_name_list[0]

    # NOTE: usage with Key=something, Value=something is deprecated
    # NOTE: inst_filter is either None or dict
    @lmi_return_val_if_fail(lambda obj: obj._namespace, [])
    def instances(self, inst_filter=None, **kwargs):
        """
        Returns a list of objects of LMIInstance.

        Arguments:
            inst_filter -- dictionary containing filter values. The key corresponds to the
                key of CIMInstance; value contains the filtering value.

        Keyword Arguments (deprecated):
            Key, key -- filtering key, see above
            Value, value -- filtering value, see above
        """
        (instance_list, _, errorstr) = self._conn._client._get_instances(
            self._cim_classname, self._namespace.name, inst_filter, **kwargs)
        if not instance_list:
            return []
        return map(lambda instance: lmi_wrap_cim_instance(self._conn,
            instance, instance.classname, instance.path.namespace),
            instance_list)

    # NOTE: usage with Key=something, Value=something is deprecated
    # NOTE: inst_filter is either None or dict
    def first_instance(self, inst_filter=None, **kwargs):
        """
        Returns the first LMIInstance of the corresponding class.

        Arguments:
            inst_filter -- dictionary containing filter values. The key corresponds to the
                key of CIMInstance; value contains the filtering value.

        Keyword Arguments (deprecated):
            Key, key -- filtering key, see above
            Value, value -- filtering value, see above
        """
        filter_value = "value" in [k.lower() for k in kwargs.keys()]
        if inst_filter or filter_value:
            (instance_list, _, errorstr) = self._conn._client._get_instances(
                self._cim_classname, self._namespace.name, inst_filter, **kwargs)
            if not instance_list:
                return None
            instance = instance_list[0]
            return lmi_wrap_cim_instance(self._conn, instance, instance.classname,
                instance.path.namespace)
        inst_name = self.first_instance_name(inst_filter, **kwargs)
        return inst_name.to_instance() if inst_name else None

    @lmi_class_fetch_lazy
    @lmi_return_val_if_fail(lambda obj: obj._namespace, [])
    def valuemap_properties(self):
        """
        Returns a list of strings of the constant names.
        """
        return self._valuemap_properties_list

    @lmi_class_fetch_lazy
    @lmi_return_if_fail(lambda obj: obj._namespace)
    def print_valuemap_properties(self):
        """
        Prints out the list of string of constant names.
        """
        for i in self._valuemap_properties_list:
            sys.stdout.write("%s\n" % i)

    @lmi_class_fetch_lazy
    @lmi_return_val_if_fail(lambda obj: obj._namespace, [])
    def properties(self):
        """
        Returns a list of strings of the CIMClass properties.
        """
        return self._cim_class.properties.keys()

    @lmi_class_fetch_lazy
    @lmi_return_if_fail(lambda obj: obj._namespace)
    def print_properties(self):
        """
        Prints out the list of CIMClass properties.
        """
        for prop in self._cim_class.properties.keys():
            sys.stdout.write("%s\n" % prop)

    @lmi_class_fetch_lazy
    @lmi_return_val_if_fail(lambda obj: obj._namespace, [])
    def methods(self):
        """
        Returns a list of strings of CIMClass methods.
        """
        return self._cim_class.methods.keys()

    @lmi_class_fetch_lazy
    @lmi_return_if_fail(lambda obj: obj._namespace)
    def print_methods(self):
        """
        Prints out the list of CIMClass methods.
        """
        for method in self._cim_class.methods.keys():
            sys.stdout.write("%s\n" % method)

    @property
    def classname(self):
        """
        Property returning a string of a CIMClass class name.
        """
        return self._cim_classname

    @property
    @lmi_return_val_if_fail(lambda obj: obj._namespace, "Unknown")
    def namespace(self):
        """
        Property returning a string of the namespace name.
        """
        return self._namespace.name
