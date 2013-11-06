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

from LMIObjectFactory import LMIObjectFactory
from LMIReturnValue import LMIReturnValue
from LMIUtil import lmi_raise_or_dump_exception

from LMIExceptions import LMIFilterError

class LMIBaseClient(object):
    """
    Base client class for CIMOM communication. It abstracts the :py:mod:`pywbem` dependent
    calls to :py:class:`LMIBaseClient` API.

    :param string uri: URI of the CIMOM
    :param string username: account, under which, the CIM calls will be performed
    :param string password: user's password
    :param conn_type: type of connection; can be of 2 values:

      * :py:attr:`LMIBaseClient.CONN_TYPE_WBEM` -- WBEM connection
      * :py:attr:`LMIBaseClient.CONN_TYPE_PEGASUS_UDS` -- applicable only for
        Tog-Pegasus CIMOM, it uses Unix socket for the connection; default value is
        :py:attr:`LMIbaseClient.CONN_TYPE_WBEM`

    :param string key_file: path to x509 key file; default value is None
    :param string cert_file: path to x509 cert file; default value is None
    :param bool verify_server_cert: indicates, whether a server side certificate needs to
        be verified, if SSL used; default value is True
    """
    QUERY_LANG_CQL = "DMTF:CQL"
    QUERY_LANG_WQL = "WQL"
    CONN_TYPE_WBEM, \
    CONN_TYPE_PEGASUS_UDS = range(2)

    def __init__(self, uri, username="", password="", **kwargs):
        def verify_callback(conn, cert, errno, errdepth, rcode):
            """
            Callback function used to verify the server certificate. It is passed to
            OpenSSL.SSL.set_verify, and is called during the SSL handshake. This function
            returns True, if verification passes and False otherwise.

            :param conn: Connection object
            :param cert: x509 object
            :param int errno: potential error number
            :param int errdepth: error depth
            :param int rcode: return code
            :returns: True, if certificate was successfully verified; False otherwise

            **NOTE:** see :py:class:`pywbem.cim_operations.WBEMConnection`
            """
            return bool(rcode)

        # Set remaining arguments
        conn_type = kwargs.pop("conn_type", LMIBaseClient.CONN_TYPE_WBEM)
        verify_server_cert = kwargs.pop("verify_server_cert", True)
        key_file = kwargs.pop("key_file", None)
        cert_file = kwargs.pop("cert_file", None)
        if kwargs:
            raise TypeError("__init__() got an unexpected keyword arguments: %s" % ", ".join(kwargs.keys()))

        self._uri = uri
        self._username = username
        if not self._uri.startswith("http://") and not self._uri.startswith("https://"):
            self._uri= "https://" + self._uri
        if conn_type == LMIBaseClient.CONN_TYPE_PEGASUS_UDS:
            self._cliconn = pywbem.PegasusUDSConnection()
        else:
            self._cliconn = pywbem.WBEMConnection(self._uri,
                (self._username, password),
                x509={"key_file" : key_file, "cert_file" : cert_file},
                verify_callback=verify_callback if verify_server_cert else None
            )

    # NOTE: usage with Key=something, Value=something is deprecated
    # NOTE: inst_filter is either None or dict
    def _get_instance_names(self, class_name, namespace=None, inst_filter=None, **kwargs):
        """
        Returns a list of :py:class:`CIMInstanceName` objects.

        :param string class_name: class name
        :param string namespace: namespace name, where the instance names live
        :param dictionary inst_filter: dictionary containing filter values. The key
            corresponds to the primary key of the :py:class:`CIMInstanceName`; value contains
            the filtering value.
        :param dictionary kwargs: supported keyword arguments (these are **deprecated**)

            * **Key** or **key** (*string*) -- filtering key, see above
            * **Value** or **value** (*string*) -- filtering value, see above

        :returns: :py:class:`LMIReturnValue` object with ``rval`` contains a list of
            :py:class:`CIMInstanceName` objects, if no error occurs; otherwise ``rval`` is
            set to None and ``errorstr`` contains appropriate error string
        :raises: :py:exc:`.LMIFilterError`,
            :py:exc:`pywbem.CIMError`, :py:exc:`pywbem.AuthError`
        """
        filter_value = ""
        filter_key = "Name"
        if inst_filter is None:
            inst_filter = {}
        if "key" in kwargs:
            filter_key = kwargs["key"]
            kwargs.pop("key")
        elif "Key" in kwargs:
            filter_key = kwargs["Key"]
            kwargs.pop("Key")
        if "value" in kwargs:
            filter_value = kwargs["value"]
            kwargs.pop("value")
        if "Value" in kwargs:
            filter_value = kwargs["Value"]
            kwargs.pop("Value")
        if filter_value:
            inst_filter[filter_key] = filter_value
        try:
            inst_name_list = self._cliconn.EnumerateInstanceNames(class_name, namespace, **kwargs)
            if inst_filter:
                inst_name_list_filtered = []
                for inst_name in inst_name_list:
                    append = True
                    for (filter_key, filter_value) in inst_filter.iteritems():
                        if inst_name[filter_key] != filter_value:
                            append = False
                            break
                    if append:
                        inst_name_list_filtered.append(inst_name)
                inst_name_list = inst_name_list_filtered
        except KeyError, e:
            errorstr = "Can not filter by '%s'" % filter_key
            lmi_raise_or_dump_exception(LMIFilterError(errorstr))
            return LMIReturnValue(rval=None, errorstr=errorstr)
        except pywbem.cim_operations.CIMError, e:
            lmi_raise_or_dump_exception(e)
            return LMIReturnValue(rval=None, errorstr=e.args[1])
        except pywbem.cim_http.AuthError, e:
            lmi_raise_or_dump_exception(e)
            return LMIReturnValue(rval=None, errorstr=e.args[0])
        return LMIReturnValue(rval=inst_name_list)

    def _get_instance(self, path, **kwargs):
        """
        Returns a :py:class:`CIMInstance` object.

        :param CIMInstanceName path: path of the object, which is about to be retrieved
        :param bool LocalOnly: indicates if to include the only elements (properties,
            methods, references) overridden or defined in the class
        :param bool IncludeQualifiers: indicates, if all Qualifiers for the class and its
            elements shall be included in the response
        :param bool IncludeClassOrigin: indicates, if the ``CLASSORIGIN`` attribute shall
            be present on all appropriate elements in the returned class
        :param list PropertyList: if present and not None, the members of the list define
            one or more property names. The returned class shall not include elements for
            properties missing from this list. Note that if LocalOnly is specified as
            True, it acts as an additional filter on the set of properties returned. For
            example, if property A is included in the PropertyList but LocalOnly is set to
            True and A is not local to the requested class, it is not included in the
            response. If the PropertyList input parameter is an empty list, no properties
            are included in the response. If the PropertyList input parameter is None, no
            additional filtering is defined.

        :returns: :py:class:`LMIReturnValue` object, where ``rval`` is set to
            :pyclass:`CIMInstance` object, if no error occurs; otherwise ``errorstr`` is set
            to corresponding error string
        :raises: :py:exc:`pywbem.CIMError`, :py:exc:`pywbem.AuthError`
        """
        if isinstance(path, LMIObjectFactory().LMIInstanceName):
            path = path.wrapped_object
        try:
            inst = self._cliconn.GetInstance(path, **kwargs)
        except pywbem.cim_operations.CIMError, e:
            lmi_raise_or_dump_exception(e)
            return LMIReturnValue(rval=None, errorstr=e.args[1])
        except pywbem.cim_http.AuthError, e:
            lmi_raise_or_dump_exception(e)
            return LMIReturnValue(rval=None, errorstr=e.args[0])
        return LMIReturnValue(rval=inst)

    # NOTE: usage with Key=something, Value=something is deprecated
    # NOTE: inst_filter is either None or dict
    def _get_instances(self, class_name, namespace=None, inst_filter=None, **kwargs):
        """
        Returns a list of :py:class:`CIMInstance` objects.

        :param string class_name: class name
        :param string namespace: namespace, where the instances live
        :param dictionary inst_filter: dictionary containing filter values. The key
            corresponds to the primary key of the :py:class:`CIMInstanceName`;
            value contains the filtering value.
        :param dictionary kwargs: supported keyword arguments (these are **deprecated**)

            * **Key** or **key** (*string*) -- filtering key, see above
            * **Value** or **value** (*string*) -- filtering value, see above

        :returns: :py:class:`LMIReturnValue` object with ``rval`` set to a list of
            :py:class:`CIMIntance` objects, if no error occurs; otherwise
            ``rval`` is set to None and ``errorstr`` is set to corresponding
            error string.
        :raises: :py:exc:`pywbem.CIMError`, :py:exc:`pywbem.AuthError`
        """
        filter_value = ""
        filter_key = "Name"
        if inst_filter is None:
            inst_filter = {}
        if "key" in kwargs:
            filter_key = kwargs["key"]
            kwargs.pop("key")
        elif "Key" in kwargs:
            filter_key = kwargs["Key"]
            kwargs.pop("Key")
        if "value" in kwargs:
            filter_value = kwargs["value"]
            kwargs.pop("value")
        if "Value" in kwargs:
            filter_value = kwargs["Value"]
            kwargs.pop("Value")
        if filter_value:
            inst_filter[filter_key] = filter_value
        query = "select * from %s" % class_name
        if inst_filter:
            more = False
            query += " where"
            for (filter_key, filter_value) in inst_filter.iteritems():
                if more:
                    query += " and"
                quotes = isinstance(filter_value, basestring)
                query += " %s =" % filter_key
                query += " \"%s\"" % filter_value if quotes else " %s" % filter_value
                more = True
        (inst_list, _, errorstr) = self._exec_query(LMIBaseClient.QUERY_LANG_WQL, query, namespace)
        if not inst_list:
            return LMIReturnValue(rval=None, errorstr=errorstr)
        return LMIReturnValue(rval=inst_list)

    def _get_class_names(self, namespace=None, **kwargs):
        """
        Returns a list of class names.

        :param string namespace: namespace, from which the class names list
            should be retrieved; if None, default namespace will be used (**NOTE:** see
            :py:mod:`pywbem`)
        :param string ClassName: defines the class that is the basis for the enumeration.
            If the ClassName input parameter is absent, this implies that the names of all
            classes. Default value is None.
        :param bool DeepInheritance: if not present, of False, only the names of immediate
            child subclasses are returned, otherwise the names of all subclasses of the
            specified class should be returned. Default value is False.
        :returns: :py:class:`LMIReturnValue` object with ``rval`` set to a list of strings
            containing class names, if no error occurs; otherwise ``rval`` is set to None
            and ``errorstr`` contains an appropriate error string
        :raises: :py:exc:`pywbem.CIMError`, :py:exc:`pywbem.AuthError`
        """
        try:
            class_name_list = self._cliconn.EnumerateClassNames(namespace, **kwargs)
        except pywbem.cim_operations.CIMError, e:
            lmi_raise_or_dump_exception(e)
            return LMIReturnValue(rval=None, errorstr=e.args[1])
        except pywbem.cim_http.AuthError, e:
            lmi_raise_or_dump_exception(e)
            return LMIReturnValue(rval=None, errorstr=e.args[0])
        return LMIReturnValue(rval=class_name_list)

    def _get_classes(self, namespace=None, **kwargs):
        """
        Returns a :py:class:`CIMClass` object.

        :param string namespace: namespace, from which the class names list
            should be retrieved; if None, default namespace will be used (**NOTE:** see
            :py:mod:`pywbem`)
        :param string ClassName: defines the class that is the basis for the enumeration.
            If the ClassName input parameter is absent, this implies that the names of all
            classes. Default value is None.
        :param bool DeepInheritance: if not present, of False, only the names of immediate
            child subclasses are returned, otherwise the names of all subclasses of the
            specified class should be returned. Default value is False.
        :param bool LocalOnly: indicates, if any CIM elements (properties, methods, and
            qualifiers) except those added or overridden in the class as specified in the
            classname input parameter shall not be included in the returned class.
        :param bool IncludeQualifiers: indicates, if all qualifiers for each class
            (including qualifiers on the class and on any returned properties, methods, or
            method parameters) shall be included as ``<QUALIFIER>`` elements in the
            response.
        :param bool IncludeClassOrigin: indicates, if the ``CLASSORIGIN`` attribute shall
            be present on all appropriate elements in each returned class.
        :returns: :py:class:`LMIReturnValue` object with ``rval`` set to a list of
            :py:class:`CIMClass` objects, if no error occurs; otherwise ``rval`` is set to
            None and ``errorstr`` to appropriate error string
        :raises: :py:exc:`pywbem.CIMError`, :py:exc:`pywbem.AuthError`
        """
        try:
            class_list = self._cliconn.EnumerateClasses(namespace, **kwargs)
        except pywbem.cim_operations.CIMError, e:
            lmi_raise_or_dump_exception(e)
            return LMIReturnValue(rval=None, errorstr=e.args[1])
        except pywbem.cim_http.AuthError, e:
            lmi_raise_or_dump_exception(e)
            return LMIReturnValue(rval=None, errorstr=e.args[0])
        return LMIReturnValue(rval=class_list)

    def _get_class(self, class_name, namespace=None, **kwargs):
        """
        Returns a :py:class:`CIMClass` object.

        :param string class_name: class name
        :param string namespace: -- namespace name, from which the :py:class:`CIMClass`
            should be retrieved; if None, default namespace will be used (**NOTE:** see
            :py:mod:`pywbem`)
        :param bool LocalOnly: indicates, if only local members should be present in the
            returned :py:class:`CIMClass`; any CIM elements (properties, methods, and
            qualifiers), except those added or overridden in the class as specified in the
            classname input parameter, shall not be included in the returned class.
            Default value is True.
        :param bool IncludeQualifiers: indicates, if qualifiers for the class (including
            qualifiers on the class and on any returned properties, methods, or method
            parameters) shall be included in the response. Default value is True.
        :param bool IncludeClassOrigin: indicates, if the ``CLASSORIGIN`` attribute shall
            be present on all appropriate elements in the returned class. Default value is
            False.
        :param list PropertyList: if present and not None, the members of the list define
            one or more property names. The returned class shall not include elements for
            properties missing from this list. Note that if LocalOnly is specified as
            True, it acts as an additional filter on the set of properties returned. For
            example, if property A is included in the PropertyList but LocalOnly is set to
            True and A is not local to the requested class, it is not included in the
            response. If the PropertyList input parameter is an empty list, no properties
            are included in the response. If the PropertyList input parameter is None, no
            additional filtering is defined. Default value is None.
        :returns: :py:class:`LMIReturnValue` object with rval set to
            :py:class:`CIMClass`, if no error occurs; otherwise rval is set to
            none and errorstr to appropriate error string
        :raises: :py:exc:`pywbem.CIMError`, :py:exc:`pywbem.AuthError`
        """
        try:
            klass = self._cliconn.GetClass(class_name, namespace, **kwargs)
        except pywbem.cim_operations.CIMError, e:
            lmi_raise_or_dump_exception(e)
            return LMIReturnValue(rval=None, errorstr=e.args[1])
        except pywbem.cim_http.AuthError, e:
            lmi_raise_or_dump_exception(e)
            return LMIReturnValue(rval=None, errorstr=e.args[0])
        return LMIReturnValue(rval=klass)

    def _get_superclass(self, class_name, namespace=None):
        """
        Returns a superclass to given class.

        :param string class_name: class name
        :param string namespace: namespace name
        :returns: superclass to given class, if such superclass exists,
            None otherwise
        :raises: :py:exc:`pywbem.CIMError`, :py:exc:`pywbem.AuthError`
        """
        (minimal_class, _, _) = LMIBaseClient._get_class(self, class_name, namespace,
            LocalOnly=True, IncludeQualifiers=False, PropertyList=[])
        if not minimal_class:
            return None
        return minimal_class.superclass

    def _call_method_raw(self, instance, method, **params):
        """
        Executes a method within a given :py:class:`CIMInstance`.

        :param CIMInstance instance: object, on which the method will be issued
        :param string method: string containing a method name
        :param dictionary params: parameters passed to the method call
        :returns: :py:class:`LMIReturnValue` object with rval set to return value of the
            method call, rparams set to returned parameters from the method call, if no
            error occurs; otherwise rval is set to -1 and errorstr to appropriate error
            string
        :raises: :py:exc:`pywbem.CIMError`, :py:exc:`pywbem.AuthError`
        """
        if isinstance(instance, LMIObjectFactory().LMIInstance):
            instance = instance.wrapped_object
        try:
            (rval, rparams) = self._cliconn.InvokeMethod(method, instance.path, **params)
        except pywbem.cim_operations.CIMError, e:
            lmi_raise_or_dump_exception(e)
            errorstr = e.args[1] + ": '" + method + "'"
            return LMIReturnValue(rval=-1, errorstr=errorstr)
        except pywbem.cim_http.AuthError, e:
            lmi_raise_or_dump_exception(e)
            errorstr = e.args[0] + ": '" + method + "'"
            return LMIReturnValue(rval=-1, errorstr=errorstr)
        return LMIReturnValue(rval=rval, rparams=rparams)

    def _call_method(self, instance, method, **params):
        """
        Executes a method within a given :py:class:`CIMInstance`.

        :param CIMInstance instance: object, on which the method will be issued
        :param string method: a method name
        :param dictionary params: parameters passed to the method call
        :returns: :py:class:`LMIReturnValue` object with ``rval`` set to True,
            rparams set to returned parameters from the method call, if no
            error occurs; otherwise ``rval`` is set to False and ``errorstr``
            to appropriate error string
        :raises: :py:exc:`pywbem.CIMError`, :py:exc:`pywbem.AuthError`
        """
        (rval, rparams, errorstr) = self._call_method_raw(instance, method, **params)
        return LMIReturnValue(rval=(rval == 0), rparams=rparams, errorstr=errorstr)

    def _get_associator_names(self, instance, **kwargs):
        """
        Returns a list of associated :py:class:`CIMInstanceName` objects with an input
        instance.

        :param CIMInstance instance: for this object the list of associated
            :py:class:`CIMInstanceName` will be returned
        :param string AssocClass: valid CIM association class name. It acts as a filter on
            the returned set of names by mandating that each returned name identify an
            object that shall be associated to the source object through an instance of
            this class or one of its subclasses.
        :param string ResultClass: valid CIM class name. It acts as a filter on x the
            returned set of names by mandating that each returned name identify an object
            that shall be either an instance of this class (or one of its subclasses) or
            be this class (or one of its subclasses).
        :param string Role: valid property name. It acts as a filter on the returned set
            of names by mandating that each returned name identify an object that shall be
            associated to the source object through an association in which the source
            object plays the specified role. That is, the name of the property in the
            association class that refers to the source object shall match the value of
            this parameter.
        :param string ResultRole: valid property name. It acts as a filter on the returned
            set of names by mandating that each returned name identify an object that
            shall be associated to the source object through an association in which the
            named returned object plays the specified role. That is, the name of the
            property in the association class that refers to the returned object shall
            match the value of this parameter.
        :returns: list of associated :py:class:`CIMInstanceName` objects with
            an input instance, if no error occurs; otherwise en empty list is
            returned
        :raises: :py:exc:`pywbem.CIMError`, :py:exc:`pywbem.AuthError`
        """
        if isinstance(instance, LMIObjectFactory().LMIInstance):
            instance = instance.wrapped_object
        try:
            return self._cliconn.AssociatorNames(instance.path, **kwargs)
        except (pywbem.cim_operations.CIMError, pywbem.cim_http.AuthError), e:
            lmi_raise_or_dump_exception(e)
            return []

    def _get_associators(self, instance, **kwargs):
        """
        Returns a list of associated :py:class:`CIMInstance` objects with an
        input instance.

        :param CIMInstance instance: for this object the list of associated
            :py:class:`CIMInstance` objects will be returned
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
        :param bool IncludeQualifiers: indicates, if all qualifiers for each object
            (including qualifiers on the object and on any returned properties) shall be
            included as ``<QUALIFIER>`` elements in the response. Default value is False.
        :param bool IncludeClassOrigin: indicates, if the ``CLASSORIGIN`` attribute shall
            be present on all appropriate elements in each returned object. Default value
            is False.
        :param list PropertyList: if not None, the members of the array define one or more
            property names. Each returned object shall not include elements for any
            properties missing from this list. If PropertyList is an empty list, no
            properties are included in each returned object. If it is None, no additional
            filtering is defined. Default value is None.
        :returns: list of associated :py:class:`CIMInstance` objects with an input
            instance, if no error occurs; otherwise an empty list is returned
        :raises: :py:exc:`pywbem.CIMError`, :py:exc:`pywbem.AuthError`
        """
        if isinstance(instance, LMIObjectFactory().LMIInstance):
            instance = instance.wrapped_object
        try:
            return self._cliconn.Associators(instance.path, **kwargs)
        except (pywbem.cim_operations.CIMError, pywbem.cim_http.AuthError), e:
            lmi_raise_or_dump_exception(e)
            return []

    def _get_reference_names(self, instance, **kwargs):
        """
        Returns a list of association :py:class:`CIMInstanceName` objects.

        :param CIMInstance instance: for this object the association
            :py:class:`CIMInstanceName` objects will be returned
        :param string ResultClass: valid CIM class name. It acts as a filter on the
            returned set of object names by mandating that each returned Object Name identify
            an instance of this class (or one of its subclasses) or this class (or one of its
            subclasses).
        :param string Role: valid property name. It acts as a filter on the returned set
            of object names by mandating that each returned object name shall identify an
            object that refers to the target instance through a property with a name that
            matches the value of this parameter.
        :returns: list of association :py:class:`CIMInstanceName` objects with an input
            instance, if no error occurs; otherwise an empty list is returned
        :raises: :py:exc:`pywbem.CIMError`, :py:exc:`pywbem.AuthError`
        """
        if isinstance(instance, LMIObjectFactory().LMIInstance):
            instance = instance.wrapped_object
        try:
            return self._cliconn.ReferenceNames(instance.path, **kwargs)
        except (pywbem.cim_operations.CIMError, pywbem.cim_http.AuthError), e:
            lmi_raise_or_dump_exception(e)
            return []

    def _get_references(self, instance, **kwargs):
        """
        Returns a list of association :py:class:`CIMInstance` objects.

        :param CIMInstance instance: for this object the list of association
            :py:class:`CIMInstance` objects will be returned
        :param string ResultClass: valid CIM class name. It acts as a filter on the
            returned set of objects by mandating that each returned object shall be an
            instance of this class (or one of its subclasses) or this class (or one of its
            subclasses). Default value is None.
        :param string Role: valid property name. It acts as a filter on the returned set
            of objects by mandating that each returned object shall refer to the target
            object through a property with a name that matches the value of this
            parameter. Default value is None.
        :param bool IncludeQualifiers: bool flag indicating, if all qualifiers for each
            object (including qualifiers on the object and on any returned properties)
            shall be included as ``<QUALIFIER>`` elements in the response. Default value
            is False.
        :param bool IncludeClassOrigin: bool flag indicating, if the ``CLASSORIGIN``
            attribute shall be present on all appropriate elements in each returned
            object. Default value is False.
        :param list PropertyList: if not None, the members of the list define one or more
            property names. Each returned object shall not include elements for any
            properties missing from this list. If PropertyList is an empty list, no
            properties are included in each returned object. If PropertyList is None, no
            additional filtering is defined. Default value is None.
        :returns: list of association :py:class:`CIMInstance` objects with an input
            instance, if no error occurs; otherwise an empty list is returned
        :raises: :py:exc:`pywbem.CIMError`, :py:exc:`pywbem.AuthError`
        """
        if isinstance(instance, LMIObjectFactory().LMIInstance):
            instance = instance.wrapped_object
        try:
            return self._cliconn.References(instance.path, **kwargs)
        except (pywbem.cim_operations.CIMError, pywbem.cim_http.AuthError), e:
            lmi_raise_or_dump_exception(e)
            return []

    def _create_instance(self, classname, namespace, properties=None, qualifiers=None, property_list=None):
        """
        Creates a new :py:class:`CIMInstance` object.

        :param string classname: class name of a new instance
        :param string namespace: namespace, of the new instance
        :param dictionary properties: property names and values
        :param dictionary qualifiers: qualifier names and values
        :param list property_list: list for property filtering; see
            :py:class:`CIMInstance`
        :returns: new :class:`CIMInstance`, if no error occurs; otherwise None is returned
        :raises: :py:exc:`pywbem.CIMError`, :py:exc:`pywbem.AuthError`
        """
        # Create a new dictionaries from the input ones, we do not want to modify user's
        # input variables.
        properties = dict(properties) if not properties is None else {}
        qualifiers = dict(qualifiers) if not qualifiers is None else {}
        cim_instance = pywbem.CIMInstance(classname, properties, qualifiers,
            pywbem.CIMInstanceName(classname, namespace=namespace), property_list)
        try:
            cim_path = self._cliconn.CreateInstance(NewInstance=cim_instance)
        except pywbem.CIMError, e:
            lmi_raise_or_dump_exception(e)
            return LMIReturnValue(rval=None, errorstr=e.args[1])
        except pywbem.cim_http.AuthError, e:
            lmi_raise_or_dump_exception(e)
            return LMIReturnValue(rval=None, errorstr=e.args[0])
        return self._get_instance(cim_path, LocalOnly=False)

    def _modify_instance(self, instance, **kwargs):
        """
        Modifies a :py:class:`CIMInstance` object at CIMOM side.

        :param CIMInstance instance: object to be modified
        :param bool IncludeQualifiers: indicates, if the qualifiers are modified as
            specified in `ModifiedInstance`. Default value is True.
        :param list PropertyList: if not None, the members of the list define one or more
            property names. Only properties specified in the PropertyList are modified.
            Properties of the *ModifiedInstance* that are missing from the PropertyList
            are ignored. If the PropertyList is an empty list, no properties are modified.
            If the PropertyList is None, the set of properties to be modified consists of
            those of *ModifiedInstance* with values different from the current values in
            the instance to be modified. Default value is None.
        :returns: :py:class:`LMIReturnValue` object with ``rval`` set to 0, if no error
            occurs; otherwise ``rval`` is set to -1 and ``errorstr`` is set to corresponding
            error string.
        :raises: :py:exc:`pywbem.CIMError`, :py:exc:`pywbem.AuthError`
        """
        try:
            self._cliconn.ModifyInstance(instance, **kwargs)
        except pywbem.cim_operations.CIMError, e:
            lmi_raise_or_dump_exception(e)
            return LMIReturnValue(rval=e.args[0], errorstr=e.args[1])
        except pywbem.cim_http.AuthError, e:
            lmi_raise_or_dump_exception(e)
            return LMIReturnValue(rval=-1, errorstr=e.args[0])
        return LMIReturnValue(rval=0)

    def _delete_instance(self, instance):
        """
        Deletes a :py:class:`CIMInstance` from the CIMOM side.

        :param CIMInstance instance: object to be deleted
        :returns: :py:class:`LMIReturnValue` object with ``rval`` set to 0, if no error
            occurs; otherwise ``rval`` is set to -1 and ``errorstr`` is set to
            corresponding error string
        :raises: :py:exc:`pywbem.CIMError`, :py:exc:`pywbem.AuthError`
        """
        try:
            self._cliconn.DeleteInstance(instance)
        except pywbem.cim_operations.CIMError, e:
            lmi_raise_or_dump_exception(e)
            return LMIReturnValue(rval=e.args[0], errorstr=e.args[1])
        except pywbem.cim_http.AuthError, e:
            lmi_raise_or_dump_exception(e)
            return LMIReturnValue(rval=-1, errorstr=e.args[0])
        return LMIReturnValue(rval=0)

    def _exec_query(self, query_lang, query, namespace=None):
        """
        Executes a query and returns a list of :py:class:`CIMInstance` objects.

        :param string query_lang: query language
        :param string query: query to execute
        :param string namespace: target namespace for the query
        :returns: :py:class:`LMIReturnValue` object with ``rval`` set to list of
            :py:class:`CIMInstance` objects, if no error occurs; otherwise ``rval`` is set
            to empty list and ``errorstr`` is set to corresponding error string
        :raises: :py:exc:`pywbem.CIMError`, :py:exc:`pywbem.AuthError`
        """
        try:
            inst_list = self._cliconn.ExecQuery(query_lang, query, namespace)
        except pywbem.cim_operations.CIMError, e:
            lmi_raise_or_dump_exception(e)
            return LMIReturnValue(rval=[], errorstr=e.args[1])
        except pywbem.cim_http.AuthError, e:
            lmi_raise_or_dump_exception(e)
            return LMIReturnValue(rval=[], errorstr=e.args[0])
        return LMIReturnValue(rval=inst_list)

    @property
    def username(self):
        """
        :returns: user name as a part of provided credentials
        :rtype: string
        """
        return self._username

    @property
    def uri(self):
        """
        :returns: URI of the CIMOM
        :rtype: string
        """
        return self._uri
