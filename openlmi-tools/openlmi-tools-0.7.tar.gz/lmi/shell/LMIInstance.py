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
    LMI wrapper class representing CIMInstance.
    """
    def __init__(self, conn, lmi_class, cim_instance):
        """
        Constructs a LMIInstance object.

        Arguments:
            conn -- LMIConnection object
            lmi_class -- LMIClass object, creation class of the instance
            cim_instance -- wrapped CIMInstance object
        """
        # We use __dict__ to avoid recursion potentially caused by
        # combo __setattr__ and __getattr__
        self.__dict__["_deleted"] = False
        self.__dict__["_cim_instance"] = cim_instance
        self.__dict__["_lmi_class"] = lmi_class
        super(LMIInstance, self).__init__(conn)

    @lmi_possibly_deleted(None)
    def __getattr__(self, name):
        """
        Returns either a class member, LMIMethod object, or a CIMInstance object
        property.

        Note: If the method LMIInstance.delete() was called, this method will not execute
        its code and will return None. If the shell uses exceptions, LMIDeletedObjectError
        will be raised.

        Raised exceptions:
            LMIDeletedObjectError

        Arguments:
            name -- string containing the class member, the method name, or the property
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
        Modifies a CIMInstance property.

        Note: If the method LMIInstance.delete() was called, this method will not execute
        its code and will return None. If the shell uses exceptions, LMIDeletedObjectError
        will be raised.

        Raised exceptions:
            LMIDeletedObjectError

        Arguments:
            name -- string containing a name of the CIMInstance's member
            value -- new value
        """
        if name in self._cim_instance:
            t = self._cim_instance.properties[name].type
            self._cim_instance[name] = lmi_cast_to_cim(t, value)
        else:
            self.__dict__[name] = value

    @lmi_possibly_deleted("")
    def __repr__(self):
        """
        Returns a pretty string for the object.

        Note: If the method LMIInstance.delete() was called, this method will not execute
        its code and will return an empty string. If the shell uses exceptions,
        LMIDeletedObjectError will be raised.

        Raised exceptions:
            LMIDeletedObjectError
        """
        return "%s(classname='%s', ...)" % (self.__class__.__name__, self.classname)

    @property
    @lmi_possibly_deleted("")
    def classname(self):
        """
        Property returning a string of a class name.

        Note: If the method LMIInstance.delete() was called, this method will not execute
        its code and will return an empty string. If the shell uses exceptions,
        LMIDeletedObjectError will be raised.

        Raised exceptions:
            LMIDeletedObjectError
        """
        return self._lmi_class.classname

    @property
    @lmi_possibly_deleted("")
    def namespace(self):
        """
        Property retuning a string of a namespace name.

        Note: If the method LMIInstance.delete() was called, this method will not execute
        its code and will return an empty string. If the shell uses exceptions,
        LMIDeletedObjectError will be raised.

        Raised exceptions:
            LMIDeletedObjectError
        """
        return self._lmi_class.namespace

    @property
    @lmi_possibly_deleted(None)
    def path(self):
        """
        Property returning a string of a CIMInstance path.

        Note: If the method LMIInstance.delete() was called, this method will not execute
        its code and will return None. If the shell uses exceptions, LMIDeletedObjectError
        will be raised.

        Raised exceptions:
            LMIDeletedObjectError
        """
        return self._cim_instance.path

    @lmi_possibly_deleted(None)
    @lmi_return_if_fail(lambda obj: obj._cim_instance)
    def doc(self):
        """
        Prints out pretty verbose message with documentation for the instance. If the LMIShell
        is run in a interactive mode, the output will be redirected to a pager set by
        environment variable PAGER. If there is not PAGER set, less or more will be used
        as a fallback.

        Note: If the method LMIInstance.delete() was called, this method will not execute
        its code and will return None. If the shell uses exceptions, LMIDeletedObjectError
        will be raised.

        Raised exceptions:
            LMIDeletedObjectError
        """
        LMIXmlFormatter(self._cim_instance.tocimxml()).fancy_format(self._conn._client.interactive)

    @lmi_possibly_deleted(None)
    @lmi_return_if_fail(lambda obj: obj._cim_instance)
    def tomof(self):
        """
        Prints out a message with MOF representation of CIMMethod. If the LMIShell
        is run in a interactive mode, the output will be redirected to a pager set by
        environment variable PAGER. If there is not PAGER set, less or more will be used
        as a fallback.

        Note: If the method LMIInstance.delete() was called, this method will not execute
        its code and will return None. If the shell uses exceptions, LMIDeletedObjectError
        will be raised.

        Raised exceptions:
            LMIDeletedObjectError
        """
        LMIMofFormatter(self._cim_instance.tomof()).fancy_format(self._conn._client.interactive)

    @lmi_possibly_deleted([])
    @lmi_return_val_if_fail(lambda obj: obj._cim_instance.path, [])
    def associator_names(self, **kwargs):
        """
        Returns a list of associated LMIInstanceName with this object.

        Note: If the method LMIInstance.delete() was called, this method will not execute
        its code and will return an empty list. If the shell uses exceptions,
        LMIDeletedObjectError will be raised.

        Raised exceptions:
            LMIDeletedObjectError

        Keyword Arguments:
            AssocClass -- valid CIM association class name. It acts as a filter on the
                returned set of names by mandating that each returned name identify an object
                that shall be associated to the source object through an instance of this
                class or one of its subclasses. Default value is None.
            ResultClass -- valid CIM class name. It acts as a filter on the returned set
                of names by mandating that each returned name identify an object that shall be
                either an instance of this class (or one of its subclasses) or be this class
                (or one of its subclasses). Default value is None.
            Role -- valid property name. It acts as a filter on the returned set of names
                by mandating that each returned name identify an object that shall be
                associated to the source object through an association in which the source
                object plays the specified role. That is, the name of the property in the
                association class that refers to the source object shall match the value of
                this parameter. Default value is None.
            ResultRole -- valid property name. It acts as a filter on the returned set of
                names by mandating that each returned name identify an object that shall be
                associated to the source object through an association in which the named
                returned object plays the specified role.  That is, the name of the property
                in the association class that refers to the returned object shall match the
                value of this parameter. Default value is None.
        """
        assoc_names_list = self._conn._client._get_associator_names(self._cim_instance, **kwargs)
        return map(lambda assoc_name: lmi_wrap_cim_instance_name(self._conn, assoc_name), assoc_names_list)

    @lmi_possibly_deleted(None)
    def first_associator_name(self, **kwargs):
        """
        Returns the first associated LMIInstanceName with this object.

        Note: If the method LMIInstance.delete() was called, this method will not execute
        its code and will return None. If the shell uses exceptions, LMIDeletedObjectError
        will be raised.

        Raised exceptions:
            LMIDeletedObjectError

        Keyword Arguments:
            AssocClass -- valid CIM association class name. It acts as a filter on the
                returned set of names by mandating that each returned name identify an object
                that shall be associated to the source object through an instance of this
                class or one of its subclasses. Default value is None.
            ResultClass -- valid CIM class name. It acts as a filter on the returned set
                of names by mandating that each returned name identify an object that shall be
                either an instance of this class (or one of its subclasses) or be this class
                (or one of its subclasses). Default value is None.
            Role -- valid property name. It acts as a filter on the returned set of names
                by mandating that each returned name identify an object that shall be
                associated to the source object through an association in which the source
                object plays the specified role. That is, the name of the property in the
                association class that refers to the source object shall match the value of
                this parameter. Default value is None.
            ResultRole -- valid property name. It acts as a filter on the returned set of
                names by mandating that each returned name identify an object that shall be
                associated to the source object through an association in which the named
                returned object plays the specified role.  That is, the name of the property
                in the association class that refers to the returned object shall match the
                value of this parameter. Default value is None.
        """
        result = self.associator_names(**kwargs)
        if not result:
            return None
        return result[0]

    @lmi_possibly_deleted([])
    @lmi_return_val_if_fail(lambda obj: obj._cim_instance.path, [])
    def associators(self, **kwargs):
        """
        Returns a list of associated LMIInstance with this object.

        Note: If the method LMIInstance.delete() was called, this method will not execute
        its code and will return an empty list. If the shell uses exceptions,
        LMIDeletedObjectError will be raised.

        Raised exceptions:
            LMIDeletedObjectError

        Keyword Arguments:
            AssocClass -- valid CIM association class name. It acts as a filter on the
                returned set of objects by mandating that each returned object shall be
                associated to the source object through an instance of this class or one of
                its subclasses. Default value is None.
            ResultClass -- valid CIM class name. It acts as a filter on the returned set
                of objects by mandating that each returned object shall be either an instance
                of this class (or one of its subclasses) or be this class (or one of its
                subclasses). Default value is None.
            Role -- valid property name. It acts as a filter on the returned set of
                objects by mandating that each returned object shall be associated with the
                source object through an association in which the source object plays the
                specified role. That is, the name of the property in the association class
                that refers to the source object shall match the value of this parameter.
                Default value is None.
            ResultRole -- valid property name. It acts as a filter on the returned set of
                objects by mandating that each returned object shall be associated to the
                source object through an association in which the returned object plays the
                specified role. That is, the name of the property in the association class
                that refers to the returned object shall match the value of this parameter.
                Default value is None.
            IncludeQualifiers -- bool flag indicating, if all qualifiers for each object
                (including qualifiers on the object and on any returned properties) shall
                be included as <QUALIFIER> elements in the response. Default value is
                False.
            IncludeClassOrigin -- bool flag indicating, if the CLASSORIGIN attribute shall
                be present on all appropriate elements in each returned object. Default
                value is False.
            PropertyList -- if not None, the members of the array define one or more property
                names. Each returned object shall not include elements for any properties
                missing from this list.  If PropertyList is an empty list, no properties
                are included in each returned object. If it is None, no additional
                filtering is defined. Default value is None.
        """
        associators_list = self._conn._client._get_associators(self._cim_instance, **kwargs)
        return map(lambda assoc: lmi_wrap_cim_instance(self._conn, assoc, assoc.classname, \
            assoc.path.namespace), associators_list)

    @lmi_possibly_deleted(None)
    def first_associator(self, **kwargs):
        """
        Returns the first associated LMIInstance with this object.

        Note: If the method LMIInstance.delete() was called, this method will not execute
        its code and will return None. If the shell uses exceptions, LMIDeletedObjectError
        will be raised.

        Raised exceptions:
            LMIDeletedObjectError

        Keyword Arguments:
            AssocClass -- valid CIM association class name. It acts as a filter on the
                returned set of objects by mandating that each returned object shall be
                associated to the source object through an instance of this class or one of
                its subclasses. Default value is None.
            ResultClass -- valid CIM class name. It acts as a filter on the returned set
                of objects by mandating that each returned object shall be either an instance
                of this class (or one of its subclasses) or be this class (or one of its
                subclasses). Default value is None.
            Role -- valid property name. It acts as a filter on the returned set of
                objects by mandating that each returned object shall be associated with the
                source object through an association in which the source object plays the
                specified role. That is, the name of the property in the association class
                that refers to the source object shall match the value of this parameter.
                Default value is None.
            ResultRole -- valid property name. It acts as a filter on the returned set of
                objects by mandating that each returned object shall be associated to the
                source object through an association in which the returned object plays the
                specified role. That is, the name of the property in the association class
                that refers to the returned object shall match the value of this parameter.
                Default value is None.
            IncludeQualifiers -- bool flag indicating, if all qualifiers for each object
                (including qualifiers on the object and on any returned properties) shall
                be included as <QUALIFIER> elements in the response. Default value is
                False.
            IncludeClassOrigin -- bool flag indicating, if the CLASSORIGIN attribute shall
                be present on all appropriate elements in each returned object. Default
                value is False.
            PropertyList -- if not None, the members of the array define one or more property
                names. Each returned object shall not include elements for any properties
                missing from this list.  If PropertyList is an empty list, no properties
                are included in each returned object. If it is None, no additional
                filtering is defined. Default value is None.
        """
        result = self.associators(**kwargs)
        if not result:
            return None
        return result[0]

    @lmi_possibly_deleted([])
    @lmi_return_val_if_fail(lambda obj: obj._cim_instance.path, [])
    def reference_names(self, **kwargs):
        """
        Returns a list of association LMIInstanceName objects with this object.

        Note: If the method LMIInstance.delete() was called, this method will not execute
        its code and will return an empty list. If the shell uses exceptions,
        LMIDeletedObjectError will be raised.

        Raised exceptions:
            LMIDeletedObjectError

        Keyword Arguments:
            ResultClass -- valid CIM class name. It acts as a filter on the returned set
                of object names by mandating that each returned Object Name identify an
                instance of this class (or one of its subclasses) or this class (or one of its
                subclasses). Default value is None.
            Role -- valid property name. It acts as a filter on the returned set of object
                names by mandating that each returned object name shall identify an object
                that refers to the target instance through a property with a name that matches
                the value of this parameter. Default value is None.
        """
        reference_names_list = self._conn._client._get_reference_names(self._cim_instance, **kwargs)
        return map(lambda ref_name: lmi_wrap_cim_instance_name(self._conn, ref_name), reference_names_list)

    @lmi_possibly_deleted(None)
    def first_reference_name(self, **kwargs):
        """
        Returns the first association LMIInstanceName with this object.

        Note: If the method LMIInstance.delete() was called, this method will not execute
        its code and will return None. If the shell uses exceptions, LMIDeletedObjectError
        will be raised.

        Raised exceptions:
            LMIDeletedObjectError

        Keywords Arguments:
            ResultClass -- valid CIM class name. It acts as a filter on the returned set
                of object names by mandating that each returned Object Name identify an
                instance of this class (or one of its subclasses) or this class (or one of its
                subclasses). Default value is None.
            Role -- valid property name. It acts as a filter on the returned set of object
                names by mandating that each returned object name shall identify an object
                that refers to the target instance through a property with a name that matches
                the value of this parameter. Default value is None.
        """
        result = self.reference_names(**kwargs)
        if not result:
            return None
        return result[0]

    @lmi_possibly_deleted([])
    @lmi_return_val_if_fail(lambda obj: obj._cim_instance.path, [])
    def references(self, **kwargs):
        """
        Returns a list of association LMIInstance objects with this object.

        Note: If the method LMIInstance.delete() was called, this method will not execute
        its code and will return an empty list. If the shell uses exceptions,
        LMIDeletedObjectError will be raised.

        Raised exceptions:
            LMIDeletedObjectError

        Keyword Arguments:
            ResultClass -- valid CIM class name. It acts as a filter on the returned set
                of objects by mandating that each returned object shall be an instance of this
                class (or one of its subclasses) or this class (or one of its subclasses).
                Default value is None.
            Role -- valid property name. It acts as a filter on the returned set of
                objects by mandating that each returned object shall refer to the target
                object through a property with a name that matches the value of this
                parameter. Default value is None.
            IncludeQualifiers -- bool flag indicating, if all qualifiers for each object
                (including qualifiers on the object and on any returned properties) shall be
                included as <QUALIFIER> elements in the response. Default value is False.
            IncludeClassOrigin -- bool flag indicating, if the CLASSORIGIN attribute shall
                be present on all appropriate elements in each returned object. Default
                value is False.
            PropertyList -- if not None, the members of the list define one or more property
                names. Each returned object shall not include elements for any properties
                missing from this list.  If PropertyList is an empty list, no properties
                are included in each returned object. If PropertyList is None, no
                additional filtering is defined. Default value is None.
        """
        references_list = self._conn._client._get_references(self._cim_instance, **kwargs)
        return map(lambda ref: lmi_wrap_cim_instance(self._conn, ref, ref.classname, \
            ref.path.namespace), references_list)

    @lmi_possibly_deleted(None)
    def first_reference(self, **kwargs):
        """
        Returns the first association LMIInstance with this object.

        Note: If the method LMIInstance.delete() was called, this method will not execute
        its code and will return None. If the shell uses exceptions, LMIDeletedObjectError
        will be raised.

        Raised exceptions:
            LMIDeletedObjectError

        Keyword Arguments:
            ResultClass -- valid CIM class name. It acts as a filter on the returned set
                of objects by mandating that each returned object shall be an instance of this
                class (or one of its subclasses) or this class (or one of its subclasses).
                Default value is None.
            Role -- valid property name. It acts as a filter on the returned set of
                objects by mandating that each returned object shall refer to the target
                object through a property with a name that matches the value of this
                parameter. Default value is None.
            IncludeQualifiers -- bool flag indicating, if all qualifiers for each object
                (including qualifiers on the object and on any returned properties) shall be
                included as <QUALIFIER> elements in the response. Default value is False.
            IncludeClassOrigin -- bool flag indicating, if the CLASSORIGIN attribute shall
                be present on all appropriate elements in each returned object. Default
                value is False.
            PropertyList -- if not None, the members of the list define one or more property
                names. Each returned object shall not include elements for any properties
                missing from this list.  If PropertyList is an empty list, no properties
                are included in each returned object. If PropertyList is None, no
                additional filtering is defined. Default value is None.
        """
        result = self.references(**kwargs)
        if not result:
            return None
        return result[0]

    @lmi_possibly_deleted([])
    @lmi_return_val_if_fail(lambda obj: obj._cim_instance.properties, [])
    def properties(self):
        """
        Returns a list of CIMInstance properties.

        Note: If the method LMIInstance.delete() was called, this method will not execute
        its code and will return an empty list. If the shell uses exceptions,
        LMIDeletedObjectError will be raised.

        Raised exceptions:
            LMIDeletedObjectError
        """
        return self._cim_instance.properties.keys()

    @lmi_possibly_deleted(None)
    @lmi_return_if_fail(lambda obj: obj._cim_instance.properties)
    def print_properties(self):
        """
        Prints out the list of CIMInstance properties.

        Note: If the method LMIInstance.delete() was called, this method will not execute
        its code and will return None. If the shell uses exceptions, LMIDeletedObjectError
        will be raised.

        Raised exceptions:
            LMIDeletedObjectError
        """
        for (name, prop) in self._cim_instance.properties.iteritems():
            sys.stdout.write("%s\n" % name)

    @lmi_possibly_deleted({})
    @lmi_return_val_if_fail(lambda obj: obj._cim_instance.properties, {})
    def properties_dict(self):
        """
        Returns dictionary containing property name and value pairs.
        This method may consume significant memory amount when called.

        Note: If the method LMIInstance.delete() was called, this method will not execute
        its code and will return an empty dictionary. If the shell uses exceptions,
        LMIDeletedObjectError will be raised.

        Raised exceptions:
            LMIDeletedObjectError
        """
        return pywbem.NocaseDict({
            k: x.value for k, x in self._cim_instance.properties.iteritems()})

    @lmi_possibly_deleted(None)
    def property_value(self, prop_name):
        """
        Returns a CIMInstance property value.

        Note: If the method LMIInstance.delete() was called, this method will not execute
        its code and will return None. If the shell uses exceptions, LMIDeletedObjectError
        will be raised.

        Raised exceptions:
            LMIDeletedObjectError

        Arguments:
            prop_name -- string containing the CIMInstance property name
        """
        return getattr(self, prop_name)

    @lmi_possibly_deleted([])
    def methods(self):
        """
        Returns a list of CIMInstance methods' names.

        Note: If the method LMIInstance.delete() was called, this method will not execute
        its code and will return an empty list. If the shell uses exceptions,
        LMIDeletedObjectError will be raised.

        Raised exceptions:
            LMIDeletedObjectError
        """
        return self._lmi_class.methods()

    @lmi_possibly_deleted(None)
    def print_methods(self):
        """
        Prints out the list of CIMInstance methods' names.

        Note: If the method LMIInstance.delete() was called, this method will not execute
        its code and will return None. If the shell uses exceptions, LMIDeletedObjectError
        will be raised.

        Raised exceptions:
            LMIDeletedObjectError
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
        Retreives a new CIMInstance object. Basically refreshes the object properties.
        Returns LMIReturnValue with rval set to True, if the wrapped CIMInstance object
        was refreshed; otherwise rval is set to False.

        Note: If the method LMIInstance.delete() was called, this method will not execute
        its code and will return LMIReturnValue containing False as a return value with
        proper error string set. If the shell uses exceptions, LMIDeletedObjectError will
        be raised.

        Raised exceptions:
            LMIDeletedObjectError
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
        Pushes the modified object to the CIMOM. Returns LMIReturnValue with rval set to
        0, if the modified instance was successfully pushed to the CIMOM; otherwise rval
        is set to -1.

        Note: If the method LMIInstance.delete() was called, this method will not execute
        its code and will return LMIReturnValue containing False as a return value with
        proper error string set. If the shell uses exceptions, LMIDeletedObjectError will
        be raised.

        Raised exceptions:
            LMIDeletedObjectError
        """
        (rval, rparams, errorstr) = self._conn._client._modify_instance(self._cim_instance)
        return LMIReturnValue(rval=rval, rparams=rparams, errorstr=errorstr)

    @lmi_possibly_deleted(None)
    @lmi_return_if_fail(lambda obj: obj._cim_instance.path)
    def delete(self):
        """
        Deletes this instance from the CIMOM.

        Note: If the method LMIInstance.delete() was called, this method will not execute
        its code and will return None. If the shell uses exceptions, LMIDeletedObjectError
        will be raised.

        Raised exceptions:
            LMIDeletedObjectError
        """
        rval = self._conn._client._delete_instance(self.path)
        self._deleted = rval.rval == 0

    @property
    def is_deleted(self):
        """
        Property returning a bool indicator, if the instance was deleted from the CIMOM.
        """
        return self._deleted
