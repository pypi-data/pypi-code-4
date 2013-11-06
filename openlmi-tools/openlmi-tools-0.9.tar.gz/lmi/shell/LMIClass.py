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
from LMIObjectFactory import LMIObjectFactory

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
    LMI wrapper class representing :py:class:`CIMClass`.

    :param LMIConnection conn: connection object
    :param LMINamespace namespace: namespace object
    :param string classname: CIM class name
    """
    def __init__(self, conn, namespace, classname):
        # We use __dict__ to avoid recursion potentially caused by
        # combo __setattr__ and __getattr__
        self.__dict__["_namespace"] = namespace
        self.__dict__["_cim_class"] = None
        self.__dict__["_cim_classname"] = classname
        super(LMIClass, self).__init__(conn)

    def __repr__(self):
        """
        :returns: a pretty string for the object
        """
        return "%s(classname='%s', ...)" % (self.__class__.__name__, self.classname)

    @lmi_class_fetch_lazy
    def __getattr__(self, name):
        """
        Returns either a class member, or a constant value.

        Simplifies the code and constant value can be retrieved by
        :samp:`object.constant_value`.

        :param string name: object member or constant values member
        :returns: class member of :py:class:`LMIConstantValuesParamProp` object
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
        Creates a new :py:class:`CIMInstance` at the server side and returns
        :py:class:`LMIReturnValue` object containing :py:class:`LMIInstance` as a result.

        :param dictionary properties: initial properties with corresponding values
        :param dictionary qualifiers: initial qualifiers
        :param list property_list: list of properties, which should be present in
            :py:class:`LMIInstance` object

        **Usage:** See :ref:`class_create_instance`.
        """
        # No need to copy dictionaries to avoid the variable mix-up, the copying is done in
        # LMIBaseClient._create_instance(), we just pass what we get.
        properties = properties if not properties is None else {}
        qualifiers = qualifiers if not qualifiers is None else {}
        self_properties = self._cim_class.properties
        for (key, value) in properties.iteritems():
            if not key in self._cim_class.properties:
                errorstr = "No such instance property '%s'" % key
                lmi_raise_or_dump_exception(LMIUnknownPropertyError(errorstr))
                return None
            if isinstance(value, LMIObjectFactory().LMIInstanceName):
                value = value.wrapped_object
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
        Prints out pretty verbose message with documentation for the class. If the
        LMIShell is run in a interactive mode, the output will be redirected to a pager
        set by environment variable :envvar:`PAGER`. If there is not :envvar:`PAGER` set,
        less or more will be used as a fall-back.
        """
        LMIXmlFormatter(self._cim_class.tocimxml()).fancy_format(self._conn._client.interactive)

    def fetch(self):
        """
        Manually fetches a wrapped :py:class:`CIMClass` object.

        **Usage:** See :ref:`class_fetching_a_class`.
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

        :param dictionary inst_filter: filter values. The key corresponds to the primary
            key of the :py:class:`CIMInstanceName`; value contains the filtering value
        :param dictionary kwargs: deprecated keyword arguments

            * **Key** or **key** (*string*) -- filtering key, see above
            * **Value** or **value** -- filtering value, see above

        :returns: :py:class:`LMIReturnValue` object with ``rval`` set to a list of
            :py:class:`LMIInstanceName` objects

        **Usage:** See :ref:`class_get_instance_names` and :ref:`class_instance_filtering`.
        """
        (inst_name_list, _, errorstr) = self._conn._client._get_instance_names(
            self._cim_classname, self._namespace.name, inst_filter, **kwargs)
        if not inst_name_list:
            return []
        return map(lambda inst_name: lmi_wrap_cim_instance_name(self._conn, inst_name), inst_name_list)

    def new_instance_name(self, keybindings):
        """
        Create new :py:class:`LMIInstanceName` object by passing all the
            keys/values of the object.

        :param dictionary keybindings: primary keys of instance name with corresponding
            values
        :returns: new :py:class:`LMIInstanceName` object

        **Usage:** See :ref:`class_new_instance_name`.
        """
        kbs = pywbem.NocaseDict()
        for key, value in keybindings.iteritems():
            if isinstance(value, LMIObjectFactory().LMIInstanceName):
                value = value.wrapped_object
            kbs[key] = value
        cim_inst_name = pywbem.CIMInstanceName(self.classname, kbs,
            namespace=self.namespace)
        return lmi_wrap_cim_instance_name(self._conn, cim_inst_name)

    # NOTE: usage with Key=something, Value=something is deprecated
    # NOTE: inst_filter is either None or dict
    def first_instance_name(self, inst_filter=None, **kwargs):
        """
        Returns the first :py:class:`LMIInstanceName` of the corresponding
        class.

        :param dictionary inst_filter: filter values, where the key corresponds to the
            primary key of :py:class:`CIMInstanceName`; value contains the filtering
            value
        :param dictionary kwargs: deprecated keyword arguments

            * **Key** or **key** (*string*) -- filtering key, see above
            * **Value** or **value** -- filtering value, see above

        :returns: first :py:class:`LMIInstanceName` object

        **Usage:** See :ref:`class_get_instance_names` and :ref:`class_instance_filtering`.
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
        Returns a list of objects of :py:class:`LMIInstance`.

        :param dictionary inst_filter: filter values, where the key corresponds to the key
            of :py:class:`CIMInstance`; value contains the filtering value
        :param dictionary kwargs: deprecated keyword arguments

            * **Key** or **key** (*string*) -- filtering key, see above
            * **Value** or **value** -- filtering value, see above

        :returns: list of :py:class:`LMIInstance` objects

        **Usage:** See :ref:`class_get_instances` and :ref:`class_instance_filtering`.
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
        Returns the first :py:class:`LMIInstance` of the corresponding class.

        :param dictionary inst_filter: filter values, where the key corresponds to the key
            of :py:class:`CIMInstance`; value contains the filtering value.
        :param dictionary kwargs: deprecated keyword arguments

            * **Key** or **key** -- filtering key, see above
            * **Value** or **value** -- filtering value, see above

        :returns: first :py:class:`LMIInstance` object

        **Usage:** See :ref:`class_get_instances` and :ref:`class_instance_filtering`.
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
        :returns: list of strings of the constant names

        **Usage:** :ref:`class_valuemap_properties`.
        """
        return self._valuemap_properties_list

    @lmi_class_fetch_lazy
    @lmi_return_if_fail(lambda obj: obj._namespace)
    def print_valuemap_properties(self):
        """
        Prints out the list of string of constant names.

        **Usage:** :ref:`class_valuemap_properties`.
        """
        for i in self._valuemap_properties_list:
            sys.stdout.write("%s\n" % i)

    @lmi_class_fetch_lazy
    @lmi_return_val_if_fail(lambda obj: obj._namespace, [])
    def properties(self):
        """
        :returns: list of strings of the :py:class:`CIMClass` properties

        **Usage:** See :ref:`class_properties`.
        """
        return self._cim_class.properties.keys()

    @lmi_class_fetch_lazy
    @lmi_return_if_fail(lambda obj: obj._namespace)
    def print_properties(self):
        """
        Prints out the list of :py:class:`CIMClass` properties.

        **Usage:** See :ref:`class_properties`.
        """
        for prop in self._cim_class.properties.keys():
            sys.stdout.write("%s\n" % prop)

    @lmi_class_fetch_lazy
    @lmi_return_val_if_fail(lambda obj: obj._namespace, [])
    def methods(self):
        """
        :returns: list of strings of :py:class:`CIMClass` methods.

        **Usage:** See :ref:`class_methods`.
        """
        return self._cim_class.methods.keys()

    @lmi_class_fetch_lazy
    @lmi_return_if_fail(lambda obj: obj._namespace)
    def print_methods(self):
        """
        Prints out the list of :py:class:`CIMClass` methods.

        **Usage:** See :ref:`class_methods`.
        """
        for method in self._cim_class.methods.keys():
            sys.stdout.write("%s\n" % method)

    @property
    def classname(self):
        """
        :returns: class name
        :rtype: string
        """
        return self._cim_classname

    @property
    @lmi_return_val_if_fail(lambda obj: obj._namespace, "Unknown")
    def namespace(self):
        """
        :returns: namespace name
        :rtype: string
        """
        return self._namespace.name

    @property
    @lmi_class_fetch_lazy
    def wrapped_object(self):
        """
        :returns: wrapped :py:class:`CIMClass` object
        """
        return self._cim_class
