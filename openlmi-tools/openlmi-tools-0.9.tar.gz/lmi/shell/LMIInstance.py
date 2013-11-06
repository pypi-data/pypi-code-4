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
from LMIFormatter import LMIXmlFormatter
from LMIFormatter import LMIMofFormatter
from LMIObjectFactory import LMIObjectFactory
from LMIReturnValue import LMIReturnValue

from LMIDecorators import lmi_possibly_deleted
from LMIDecorators import lmi_return_expr_if_fail
from LMIDecorators import lmi_return_val_if_fail
from LMIDecorators import lmi_return_if_fail

from LMIUtil import lmi_cast_to_cim
from LMIUtil import lmi_wrap_cim_instance
from LMIUtil import lmi_wrap_cim_instance_name
from LMIUtil import lmi_wrap_cim_method

class LMIInstance(LMIWrapperBaseObject):
    """
    LMI wrapper class representing :py:class:`CIMInstance`.

    :param LMIConnection conn: connection object
    :param LMIClass lmi_class: wrapped creation class of the instance
    :param CIMInstance cim_instance: wrapped object
    """
    def __init__(self, conn, lmi_class, cim_instance):
        # We use __dict__ to avoid recursion potentially caused by
        # combo __setattr__ and __getattr__
        if isinstance(cim_instance, LMIInstance):
            cim_instance = cim_instance.wrapped_object
        self.__dict__["_deleted"] = False
        self.__dict__["_cim_instance"] = cim_instance
        self.__dict__["_lmi_class"] = lmi_class
        super(LMIInstance, self).__init__(conn)

    @lmi_possibly_deleted(False)
    def __contains__(self, key):
        """
        Returns True, if the specified key is present in the properties, False otherwise.

        **NOTE:** If the method :py:meth:``LMIInstance.delete` was called, this method
        will not execute its code and will return None. If the shell uses exceptions,
        :py:exc:`.LMIDeletedObjectError` will be raised.

        :param string key: key name, which will be tested for presence in properties
        :returns: True, if the specified key is present in properties, False otherwise
        :raises: :py:exc:`.LMIDeletedObjectError`
        """
        return key in self._cim_instance

    @lmi_possibly_deleted(None)
    def __getattr__(self, name):
        """
        Returns either a class member, :py:class:`LMIMethod` object, or a
        :py:class:`CIMInstance` object property.

        **NOTE:** If the method :py:meth:``LMIInstance.delete` was called, this method
        will not execute its code and will return None. If the shell uses exceptions,
        :py:exc:`.LMIDeletedObjectError` will be raised.

        :param string name: class member, the method name, or the property to be returned
        :returns: class member, :py:class:`LMIMethod` object or :py:class:`CIMInstance`
            object property
        :raises: :py:exc:`.LMIDeletedObjectError`
        """
        if name in self.__dict__:
            return self.__dict__[name]
        sync_method = False
        if name.startswith("Sync"):
            sync_method = True
            name = name[4:]
        methods = self.methods()
        if methods and name in methods:
            return lmi_wrap_cim_method(self._conn, name, self, sync_method)
        elif name in self._cim_instance:
            member = self._cim_instance[name]
            if isinstance(member, pywbem.CIMInstanceName):
                member = lmi_wrap_cim_instance_name(self._conn, member)
            return member
        raise AttributeError(name)

    @lmi_possibly_deleted(None)
    def __setattr__(self, name, value):
        """
        Modifies a :py:class:`CIMInstance` object property.

        **NOTE:** If the method :py:meth:`.LMIInstance.delete` was called, this method
        will not execute its code and will return None. If the shell uses exceptions,
        :py:exc:`.LMIDeletedObjectError` will be raised.

        :param string name: name of the :py:class:`CIMInstance`'s member
        :param value: new value
        :raises: :py:exc:`.LMIDeletedObjectError`
        """
        if isinstance(value, LMIObjectFactory().LMIInstanceName):
            value = value.wrapped_object
        if name in self._cim_instance:
            t = self._cim_instance.properties[name].type
            self._cim_instance[name] = lmi_cast_to_cim(t, value)
        else:
            self.__dict__[name] = value

    @lmi_possibly_deleted("")
    def __str__(self):
        """
        Returns a string of serialized :py:class:`CIMInstanceName` object.

        **NOTE:** If the method :py:meth:`.LMIInstance.delete` was called, this method
        will not execute its code and will return an empty string. If the shell uses
        exceptions, :py:exc:`.LMIDeletedObjectError` will be raised.

        :returns: string of serialized :py:class:`CIMInstanceName` object
        :raises: :py:exc:`.LMIDeletedObjectError`
        """
        return "%s(classname=\"%s\", %s)" % ( \
            self.__class__.__name__, \
            self.classname, \
            str(self._cim_instance.path) \
        )

    @lmi_possibly_deleted("")
    def __repr__(self):
        """
        Returns a pretty string for the object.

        **NOTE:** If the method :py:meth:`.LMIInstance.delete` was called, this method
        will not execute its code and will return an empty string. If the shell uses
        exceptions, :py:exc:`.LMIDeletedObjectError` will be raised.

        :returns: pretty string for the object
        :raises: :py:exc:`.LMIDeletedObjectError`
        """
        return "%s(classname=\"%s\", ...)" % (self.__class__.__name__, self.classname)

    def copy(self):
        """
        :returns: copy of itself
        """
        return lmi_wrap_cim_instance(self._conn, self._cim_instance.copy())

    @property
    @lmi_possibly_deleted("")
    def classname(self):
        """
        Property returning a string of a class name.

        **NOTE:** If the method :py:meth:`LMIInstance.delete` was called, this method will
        not execute its code and will return an empty string. If the shell uses
        exceptions, :py:exc:`.LMIDeletedObjectError` will be raised.

        :returns: class name
        :rtype: string
        :raises: :py:exc:`.LMIDeletedObjectError`
        """
        return self._lmi_class.classname

    @property
    @lmi_possibly_deleted("")
    def namespace(self):
        """
        Property retuning a string of a namespace name.

        **NOTE:** If the method :py:meth:`LMIInstance.delete` was called, this method will
        not execute its code and will return an empty string. If the shell uses
        exceptions, :py:exc:`.LMIDeletedObjectError` will be raised.

        :returns: namespace name
        :rtype: string
        :raises: :py:exc:`.LMIDeletedObjectError`
        """
        return self._lmi_class.namespace

    @property
    @lmi_possibly_deleted(None)
    def path(self):
        """
        Property returning a :py:class:`LMIInstanceName` objec5.

        **NOTE:** If the method :py:meth:`.LMIInstance.delete` was called, this method
        will not execute its code and will return None. If the shell uses exceptions,
        :py:exc:`LMIDeletedObjectError` will be raised.

        :returns: :py:class:`LMIInstanceName` object
        :raises: :py:exc:`.LMIDeletedObjectError`
        """
        return lmi_wrap_cim_instance_name(self._conn, self._cim_instance.path)

    @lmi_possibly_deleted(None)
    @lmi_return_if_fail(lambda obj: obj._cim_instance)
    def doc(self):
        """
        Prints out pretty verbose message with documentation for the instance. If the LMIShell
        is run in a interactive mode, the output will be redirected to a pager set by
        environment variable :envvar:`PAGER`. If there is not :envvar:`PAGER` set, less or
        more will be used as a fall-back.

        **NOTE:** If the method :py:meth:`LMIInstance.delete` was called, this method will
        not execute its code and will return None. If the shell uses exceptions,
        :py:exc:`.LMIDeletedObjectError` will be raised.

        :raises: :py:exc:`.LMIDeletedObjectError`
        """
        LMIXmlFormatter(self._cim_instance.tocimxml()).fancy_format(self._conn._client.interactive)

    @lmi_possibly_deleted(None)
    @lmi_return_if_fail(lambda obj: obj._cim_instance)
    def tomof(self):
        """
        Prints out a message with MOF representation of :py:class:`CIMMethod`. If
        the LMIShell is run in a interactive mode, the output will be
        redirected to a pager set by environment variable :envvar:`PAGER`. If
        there is not :envvar:`PAGER` set, less or more will be used as a
        fall-back.

        **NOTE:** If the method :py:meth:`.LMIInstance.delete` was called, this method
        will not execute its code and will return None. If the shell uses exceptions,
        :py:exc:`.LMIDeletedObjectError` will be raised.

        :raises: :py:exc:`.LMIDeletedObjectError`
        """
        LMIMofFormatter(self._cim_instance.tomof()).fancy_format(self._conn._client.interactive)

    @lmi_possibly_deleted([])
    @lmi_return_val_if_fail(lambda obj: obj._cim_instance.path, [])
    def associator_names(self, **kwargs):
        """
        Returns a list of associated :py:class:`LMIInstanceName` with this object.

        **NOTE:** If the method :py:meth:`.LMIInstance.delete` was called, this method will
        not execute its code and will return an empty list. If the shell uses exceptions,
        :py:exc:`.LMIDeletedObjectError` will be raised.

        :param string AssocClass: valid CIM association class name. It acts as a filter on
            the returned set of names by mandating that each returned name identify an
            object that shall be associated to the source object through an instance of
            this class or one of its subclasses. Default value is None.
        :param string ResultClass: valid CIM class name. It acts as a filter on the
            returned set of names by mandating that each returned name identify an object
            that shall be either an instance of this class (or one of its subclasses) or
            be this class (or one of its subclasses). Default value is None.
        :param string Role: valid property name. It acts as a filter on the returned set
            of names by mandating that each returned name identify an object that shall be
            associated to the source object through an association in which the source
            object plays the specified role. That is, the name of the property in the
            association class that refers to the source object shall match the value of
            this parameter. Default value is None.
        :param string ResultRole: valid property name. It acts as a filter on the returned
            set of names by mandating that each returned name identify an object that
            shall be associated to the source object through an association in which the
            named returned object plays the specified role. That is, the name of the
            property in the association class that refers to the returned object shall
            match the value of this parameter. Default value is None.
        :returns: list of associated :py:class:`LMIInstanceName` objects
        :raises: :py:exc:`.LMIDeletedObjectError`

        **Usage:** :ref:`associators_instance_names`.
        """
        assoc_names_list = self._conn._client._get_associator_names(self._cim_instance, **kwargs)
        return map(lambda assoc_name: lmi_wrap_cim_instance_name(self._conn, assoc_name), assoc_names_list)

    @lmi_possibly_deleted(None)
    def first_associator_name(self, **kwargs):
        """
        Returns the first associated :py:class:`LMIInstanceName` with this object.

        **NOTE:** If the method :py:meth:`.LMIInstance.delete` was called, this method will
        not execute its code and will return None. If the shell uses exceptions,
        :py:exc:`.LMIDeletedObjectError` will be raised.

        :param string AssocClass: valid CIM association class name. It acts as a filter on
            the returned set of names by mandating that each returned name identify an
            object that shall be associated to the source object through an instance of
            this class or one of its subclasses. Default value is None.
        :param string ResultClass: valid CIM class name. It acts as a filter on the
            returned set of names by mandating that each returned name identify an object
            that shall be either an instance of this class (or one of its subclasses) or
            be this class (or one of its subclasses). Default value is None.
        :param string Role: valid property name. It acts as a filter on the returned set
            of names by mandating that each returned name identify an object that shall be
            associated to the source object through an association in which the source
            object plays the specified role. That is, the name of the property in the
            association class that refers to the source object shall match the value of
            this parameter. Default value is None.
        :param string ResultRole: valid property name. It acts as a filter on the returned
            set of names by mandating that each returned name identify an object that
            shall be associated to the source object through an association in which the
            named returned object plays the specified role. That is, the name of the
            property in the association class that refers to the returned object shall
            match the value of this parameter. Default value is None.
        :returns: first associated :py:class:`LMIInstanceName` object
        :raises: :py:exc:`.LMIDeletedObjectError`

        **Usage:** :ref:`associators_instance_names`.
        """
        result = self.associator_names(**kwargs)
        if not result:
            return None
        return result[0]

    @lmi_possibly_deleted([])
    @lmi_return_val_if_fail(lambda obj: obj._cim_instance.path, [])
    def associators(self, **kwargs):
        """
        Returns a list of associated :py:class:`LMIInstance` objects with this instance.

        **NOTE:** If the method :py:meth:`.LMIInstance.delete` was called, this method will
        not execute its code and will return an empty list. If the shell uses exceptions,
        :py:exc:`.LMIDeletedObjectError` will be raised.

        :param string AssocClass: valid CIM association class name. It acts as a filter on
            the returned set of objects by mandating that each returned object shall be
            associated to the source object through an instance of this class or one of
            its subclasses. Default value is None.
        :param string ResultClass: valid CIM class name. It acts as a filter on the
            returned set of objects by mandating that each returned object shall be either
            an instance of this class (or one of its subclasses) or be this class (or one
            of its subclasses). Default value is None.
        :param string Role: valid property name. It acts as a filter on the returned set
            of objects by mandating that each returned object shall be associated with the
            source object through an association in which the source object plays the
            specified role. That is, the name of the property in the association class
            that refers to the source object shall match the value of this parameter.
            Default value is None.
        :param string ResultRole: valid property name. It acts as a filter on the returned
            set of objects by mandating that each returned object shall be associated to
            the source object through an association in which the returned object plays
            the specified role. That is, the name of the property in the association class
            that refers to the returned object shall match the value of this parameter.
            Default value is None.
        :param bool IncludeQualifiers: bool flag indicating, if all qualifiers for each
            object (including qualifiers on the object and on any returned properties)
            shall be included as ``<QUALIFIER>`` elements in the response. Default value
            is False.
        :param bool IncludeClassOrigin: bool flag indicating, if the ``CLASSORIGIN``
            attribute shall be present on all appropriate elements in each returned
            object. Default value is False.
        :param list PropertyList: if not None, the members of the array define one or more
            property names. Each returned object shall not include elements for any
            properties missing from this list. If *PropertyList* is an empty list, no
            properties are included in each returned object. If it is None, no additional
            filtering is defined. Default value is None.
        :returns: list of associated :py:class:`LMIInstance` objects
        :raises: :py:exc:`.LMIDeletedObjectError`

        **Usage:** :ref:`associators_instances`.
        """
        associators_list = self._conn._client._get_associators(self._cim_instance, **kwargs)
        return map(lambda assoc: lmi_wrap_cim_instance(self._conn, assoc, assoc.classname, \
            assoc.path.namespace), associators_list)

    @lmi_possibly_deleted(None)
    def first_associator(self, **kwargs):
        """
        Returns the first associated :py:class:`LMIInstance` with this object.

        **NOTE:** If the method :py:meth:`.LMIInstance.delete` was called, this method will
        not execute its code and will return None. If the shell uses exceptions,
        :py:exc:`.LMIDeletedObjectError` will be raised.

        :param string AssocClass: valid CIM association class name. It acts as a filter on
            the returned set of objects by mandating that each returned object shall be
            associated to the source object through an instance of this class or one of
            its subclasses. Default value is None.
        :param string ResultClass: valid CIM class name. It acts as a filter on the
            returned set of objects by mandating that each returned object shall be either
            an instance of this class (or one of its subclasses) or be this class (or one
            of its subclasses). Default value is None.
        :param string Role: valid property name. It acts as a filter on the returned set
            of objects by mandating that each returned object shall be associated with the
            source object through an association in which the source object plays the
            specified role. That is, the name of the property in the association class
            that refers to the source object shall match the value of this parameter.
            Default value is None.
        :param string ResultRole: valid property name. It acts as a filter on the returned
            set of objects by mandating that each returned object shall be associated to
            the source object through an association in which the returned object plays
            the specified role. That is, the name of the property in the association class
            that refers to the returned object shall match the value of this parameter.
            Default value is None.
        :param bool IncludeQualifiers: bool flag indicating, if all qualifiers for each
            object (including qualifiers on the object and on any returned properties)
            shall be included as ``<QUALIFIER>`` elements in the response. Default value
            is False.
        :param bool IncludeClassOrigin: bool flag indicating, if the ``CLASSORIGIN``
            attribute shall be present on all appropriate elements in each returned
            object. Default value is False.
        :param list PropertyList: if not None, the members of the array define one or more
            property names. Each returned object shall not include elements for any
            properties missing from this list. If PropertyList is an empty list, no
            properties are included in each returned object. If it is None, no additional
            filtering is defined. Default value is None.
        :returns: first associated :py:class:`LMIInstance`
        :raises: :py:exc:`.LMIDeletedObjectError`

        **Usage:** :ref:`associators_instances`.
        """
        result = self.associators(**kwargs)
        if not result:
            return None
        return result[0]

    @lmi_possibly_deleted([])
    @lmi_return_val_if_fail(lambda obj: obj._cim_instance.path, [])
    def reference_names(self, **kwargs):
        """
        Returns a list of association :py:class:`LMIInstanceName` objects with this
        object.

        **NOTE:** If the method :py:meth:`.LMIInstance.delete` was called, this method will
        not execute its code and will return an empty list. If the shell uses exceptions,
        :py:exc:`.LMIDeletedObjectError` will be raised.

        :param string ResultClass: valid CIM class name. It acts as a filter on the
            returned set of object names by mandating that each returned Object Name
            identify an instance of this class (or one of its subclasses) or this class
            (or one of its subclasses). Default value is None.
        :param string Role: valid property name. It acts as a filter on the returned set
            of object names by mandating that each returned object name shall identify an
            object that refers to the target instance through a property with a name that
            matches the value of this parameter. Default value is None.
        :returns: list of association :py:class:`LMIInstanceName` objects
        :raises: :py:exc:`.LMIDeletedObjectError`

        **Usage:** :ref:`references_instance_names`.
        """
        reference_names_list = self._conn._client._get_reference_names(self._cim_instance, **kwargs)
        return map(lambda ref_name: lmi_wrap_cim_instance_name(self._conn, ref_name), reference_names_list)

    @lmi_possibly_deleted(None)
    def first_reference_name(self, **kwargs):
        """
        Returns the first association :py:class:`LMIInstanceName` with this object.

        **NOTE:** If the method :py:meth:`.LMIInstance.delete` was called, this method will
        not execute its code and will return None. If the shell uses exceptions,
        :py:exc:`.LMIDeletedObjectError` will be raised.

        :param string ResultClass: valid CIM class name. It acts as a filter on the
            returned set of object names by mandating that each returned Object Name
            identify an instance of this class (or one of its subclasses) or this class
            (or one of its subclasses). Default value is None.
        :param string Role: valid property name. It acts as a filter on the returned set
            of object names by mandating that each returned object name shall identify an
            object that refers to the target instance through a property with a name that
            matches the value of this parameter. Default value is None.
        :returns: first association :py:class:`LMIInstanceName` object
        :raises: :py:exc:`.LMIDeletedObjectError`

        **Usage:** :ref:`references_instance_names`.
        """
        result = self.reference_names(**kwargs)
        if not result:
            return None
        return result[0]

    @lmi_possibly_deleted([])
    @lmi_return_val_if_fail(lambda obj: obj._cim_instance.path, [])
    def references(self, **kwargs):
        """
        Returns a list of association :py:class:`LMIInstance` objects with this object.

        **NOTE:** If the method :py:meth:`.LMIInstance.delete` was called, this method
        will not execute its code and will return an empty list. If the shell uses
        exceptions, :py:exc:`.LMIDeletedObjectError` will be raised.

        :param string ResultClass: valid CIM class name. It acts as a filter on the
            returned set of objects by mandating that each returned object shall be an
            instance of this class (or one of its subclasses) or this class (or one of its
            subclasses). Default value is None.
        :param string Role: valid property name. It acts as a filter on the returned set
            of objects by mandating that each returned object shall refer to the target
            object through a property with a name that matches the value of this
            parameter. Default value is None.
        :param bool IncludeQualifiers: flag indicating, if all qualifiers for each object
            (including qualifiers on the object and on any returned properties) shall be
            included as ``<QUALIFIER>`` elements in the response. Default value is False.
        :param bool IncludeClassOrigin: flag indicating, if the ``CLASSORIGIN`` attribute
            shall be present on all appropriate elements in each returned object. Default
            value is False.
        :param list PropertyList: if not None, the members of the list define one or more
            property names. Each returned object shall not include elements for any
            properties missing from this list. If PropertyList is an empty list, no
            properties are included in each returned object. If PropertyList is None, no
            additional filtering is defined. Default value is None.
        :returns: list of association :py:class:`LMIInstance` objects
        :raises: :py:exc:`.LMIDeletedObjectError`

        **Usage:** :ref:`references_instances`.
        """
        references_list = self._conn._client._get_references(self._cim_instance, **kwargs)
        return map(lambda ref: lmi_wrap_cim_instance(self._conn, ref, ref.classname, \
            ref.path.namespace), references_list)

    @lmi_possibly_deleted(None)
    def first_reference(self, **kwargs):
        """
        Returns the first association :py:class:`LMIInstance` with this object.

        **NOTE:** If the method :py:meth:`.LMIInstance.delete` was called, this method will
        not execute its code and will return None. If the shell uses exceptions,
        :py:exc:`.LMIDeletedObjectError` will be raised.

        :param string ResultClass: valid CIM class name. It acts as a filter on the
            returned set of objects by mandating that each returned object shall be an
            instance of this class (or one of its subclasses) or this class (or one of its
            subclasses). Default value is None.
        :param string Role: valid property name. It acts as a filter on the returned set
            of objects by mandating that each returned object shall refer to the target
            object through a property with a name that matches the value of this
            parameter. Default value is None.
        :param bool IncludeQualifiers: flag indicating, if all qualifiers for each object
            (including qualifiers on the object and on any returned properties) shall be
            included as ``<QUALIFIER>`` elements in the response. Default value is False.
        :param bool IncludeClassOrigin: flag indicating, if the ``CLASSORIGIN`` attribute
            shall be present on all appropriate elements in each returned object. Default
            value is False.
        :param list PropertyList: if not None, the members of the list define one or more
            property names. Each returned object shall not include elements for any
            properties missing from this list. If PropertyList is an empty list, no
            properties are included in each returned object. If PropertyList is None, no
            additional filtering is defined. Default value is None.
        :returns: first association :py:class:`LMIInstance` object
        :raises: :py:exc:`.LMIDeletedObjectError`

        **Usage:** :ref:`references_instances`.
        """
        result = self.references(**kwargs)
        if not result:
            return None
        return result[0]

    @lmi_possibly_deleted([])
    @lmi_return_val_if_fail(lambda obj: obj._cim_instance.properties, [])
    def properties(self):
        """
        Returns a list of :py:class:`CIMInstance` properties.

        **NOTE:** If the method :py:meth:`.LMIInstance.delete` was called, this method
        will not execute its code and will return an empty list. If the shell uses
        exceptions, :py:exc:`.LMIDeletedObjectError` will be raised.

        :returns: list of :py:class:`CIMInstance` properties
        :rtype: list
        :raises: :py:exc:`.LMIDeletedObjectError`

        **Usage:** :ref:`instances_properties`.
        """
        return self._cim_instance.properties.keys()

    @lmi_possibly_deleted(None)
    @lmi_return_if_fail(lambda obj: obj._cim_instance.properties)
    def print_properties(self):
        """
        Prints out the list of :py:class:`CIMInstance` properties.

        **NOTE:** If the method :py:meth:`.LMIInstance.delete` was called, this method
        will not execute its code and will return None. If the shell uses exceptions,
        :py:exc:`.LMIDeletedObjectError` will be raised.

        :raises: :py:exc:`.LMIDeletedObjectError`

        **Usage:** :ref:`instances_properties`.
        """
        for (name, prop) in self._cim_instance.properties.iteritems():
            sys.stdout.write("%s\n" % name)

    @lmi_possibly_deleted({})
    @lmi_return_val_if_fail(lambda obj: obj._cim_instance.properties, {})
    def properties_dict(self):
        """
        Returns dictionary containing property name and value pairs.
        This method may consume significant memory amount when called.

        **NOTE:** If the method :py:meth:`.LMIInstance.delete` was called, this method
        will not execute its code and will return an empty dictionary. If the shell uses
        exceptions, :py:exc:`.LMIDeletedObjectError` will be raised.

        :returns: dictionary of :py:class:`CIMInstance` properties
        :raises: :py:exc:`.LMIDeletedObjectError`
        """
        return pywbem.NocaseDict({
            k: x.value for k, x in self._cim_instance.properties.iteritems()})

    @lmi_possibly_deleted(None)
    def property_value(self, prop_name):
        """
        Returns a :py:class:`CIMInstance` property value.

        **NOTE:** If the method :py:meth:`.LMIInstance.delete` was called, this method
        will not execute its code and will return None. If the shell uses exceptions,
        :py:exc:`.LMIDeletedObjectError` will be raised.

        :param string prop_name: :py:class:`CIMInstance` property name
        :raises: :py:exc:`.LMIDeletedObjectError`
        """
        return getattr(self, prop_name)

    @lmi_possibly_deleted([])
    def methods(self):
        """
        Returns a list of :py:class:`CIMInstance` methods' names.

        **NOTE:** If the method :py:meth:`.LMIInstance.delete` was called, this method
        will not execute its code and will return an empty list. If the shell uses
        exceptions, :py:exc:`.LMIDeletedObjectError` will be raised.

        :returns: list of :py:class:`CIMInstance` methods' names
        :raises: :py:exc:`.LMIDeletedObjectError`

        **Usage:** :ref:`instances_methods`.
        """
        return self._lmi_class.methods()

    @lmi_possibly_deleted(None)
    def print_methods(self):
        """
        Prints out the list of :py:class:`CIMInstance` methods' names.

        **NOTE:** If the method :py:meth:`.LMIInstance.delete` was called, this method
        will not execute its code and will return None. If the shell uses exceptions,
        :py:exc:`.LMIDeletedObjectError` will be raised.

        :raises: :py:exc:`.LMIDeletedObjectError`

        **Usage:** :ref:`instances_methods`.
        """
        self._lmi_class.print_methods()

    @lmi_possibly_deleted( \
        LMIReturnValue(rval=False, errorstr="This instance has been deleted from a CIM broker"), \
    )
    @lmi_return_val_if_fail( \
        lambda obj: obj._cim_instance,
        LMIReturnValue(rval=False, errorstr="Can not refresh the instance"), \
    )
    def refresh(self):
        """
        Retrieves a new :py:class:`CIMInstance` object. Basically refreshes the object
        properties. Returns LMIReturnValue with rval set to True, if the wrapped
        :py:class:`CIMInstance` object was refreshed; otherwise rval is set to False.

        **NOTE:** If the method :py:meth:`.LMIInstance.delete` was called, this method
        will not execute its code and will return :py:class:`LMIReturnValue` object
        containing False as a return value with proper error string set. If the shell uses
        exceptions, :py:exc:`.LMIDeletedObjectError` will be raised.

        :returns: :py:class:`LMIReturnValue` object with ``rval`` set to True, if
            refreshed; False otherwise
        :raises: :py:exc:`.LMIDeletedObjectError`

        **Usage:** :ref:`instances_refreshing`.
        """
        (new_cim_instance, _, errorstr) = self._conn._client._get_instance(self.path, LocalOnly=False)
        if not new_cim_instance:
            return LMIReturnValue(rval=False, errorstr=errorstr)
        self._cim_instance = new_cim_instance
        return LMIReturnValue(rval=True)

    @lmi_possibly_deleted( \
        LMIReturnValue(rval=False, errorstr="This instance has been deleted from a CIM broker") \
    )
    @lmi_return_val_if_fail( \
        lambda obj: obj._cim_instance.path, \
        LMIReturnValue(rval=False, errorstr="Can't push this instance"), \
    )
    def push(self):
        """
        Pushes the modified object to the CIMOM.

        **NOTE:** If the method :py:meth:`.LMIInstance.delete` was called, this method
        will not execute its code and will return :py:class:`LMIReturnValue` object
        containing False as a return value with proper error string set. If the shell uses
        exceptions, :py:exc:`.LMIDeletedObjectError` will be raised.

        :returns: :py:class:`LMIReturnValue` object with ``rval`` set to 0, if modified;
            -1 otherwise
        :raises: :py:exc:`.LMIDeletedObjectError`

        **Usage:** :ref:`instances_properties`.
        """
        (rval, rparams, errorstr) = self._conn._client._modify_instance(self._cim_instance)
        return LMIReturnValue(rval=rval, rparams=rparams, errorstr=errorstr)

    @lmi_possibly_deleted(None)
    @lmi_return_if_fail(lambda obj: obj._cim_instance.path)
    def delete(self):
        """
        Deletes this instance from the CIMOM.

        **NOTE:** If the method :py:meth:`.LMIInstance.delete` was called, this method
        will not execute its code and will return None. If the shell uses exceptions,
        :py:exc:`.LMIDeletedObjectError` will be raised.

        :returns: True, if the instance is deleted; False otherwise
        :raises: :py:exc:`.LMIDeletedObjectError`

        **Usage:** :ref:`instances_delete`.
        """
        (rval, rparams, errorstr) = self._conn._client._delete_instance(self.path)
        self._deleted = rval == 0
        return self._deleted

    @property
    def is_deleted(self):
        """
        :returns: True, if the instance was deleted from the CIMOM; False otherwise
        """
        return self._deleted

    @property
    @lmi_possibly_deleted(None)
    def wrapped_object(self):
        """
        :returns: wrapped :py:class:`CIMInstance` object
        """
        return self._cim_instance
