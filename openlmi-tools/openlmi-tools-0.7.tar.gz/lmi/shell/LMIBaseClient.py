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

from LMIReturnValue import LMIReturnValue
from LMIUtil import lmi_raise_or_dump_exception

from LMIExceptions import LMIFilterError

class LMIBaseClient(object):
    """
    Base client class for CIMOM communication. It abstracts the pywbem dependent calls to
    LMIBaseClient api.
    """
    QUERY_LANG_CQL = "DMTF:CQL"
    QUERY_LANG_WQL = "WQL"
    CONN_TYPE_WBEM, \
    CONN_TYPE_PEGASUS_UDS = range(2)

    def __init__(self, hostname, username="", password="", **kwargs):
        """
        Constructs a LMIBaseClient object.

        Arguments:
            hostname -- uri of the CIMOM
            username -- account, under which, the CIM calls will be performed
            password -- user's password

        Keyword Arguments:
            conn_type -- type of connection; can be of 2 values:
                LMIBaseClient.CONN_TYPE_WBEM -- WBEM connection,
                LMIBaseClient.CONN_TYPE_PEGASUS_UDS -- applicable only for Tog-Pegasus
                    CIMOM, it uses unix socket for the connection; default value is
                    CONN_TYPE_WBEM
            key_file -- string containing path to x509 key file; default value is None
            cert_file -- string containing path to x509 cert file; default value is None
            verify_server_cert -- flag indicating, whether a server side certificate
                needs to be verified, if SSL used; default value is True
        """
        def verify_callback(conn, cert, errno, errdepth, rcode):
            """
            Callback function used to verify the server certificate.  It is passed to
            OpenSSL.SSL.set_verify, and is called during the SSL handshake. This function
            returns True, if verification passes and False otherwise.

            Arguments:
                conn -- a Connection object
                cert -- an X509 object
                errno --  potential error number,
                errdepth -- error depth
                rcode -- return code
            """
            return bool(rcode)

        # Set remaining arguments
        conn_type = kwargs.pop("conn_type", LMIBaseClient.CONN_TYPE_WBEM)
        verify_server_cert = kwargs.pop("verify_server_cert", True)
        key_file = kwargs.pop("key_file", None)
        cert_file = kwargs.pop("cert_file", None)
        if kwargs:
            raise TypeError("__init__() got an unexpected keyword arguments: %s" % ", ".join(kwargs.keys()))

        self._hostname = hostname
        self._username = username
        if not self._hostname.startswith("http://") and not self._hostname.startswith("https://"):
            self._hostname = "https://" + self._hostname
        if conn_type == LMIBaseClient.CONN_TYPE_PEGASUS_UDS:
            self._cliconn = pywbem.PegasusUDSConnection()
        else:
            self._cliconn = pywbem.WBEMConnection(self._hostname,
                (self._username, password),
                x509={"key_file" : key_file, "cert_file" : cert_file},
                verify_callback=verify_callback if verify_server_cert else None
            )

    # NOTE: usage with Key=something, Value=something is deprecated
    # NOTE: inst_filter is either None or dict
    def _get_instance_names(self, class_name, namespace=None, inst_filter=None, **kwargs):
        """
        Returns a LMIReturnValue object with rval contains a list of CIMInstanceNames
        objects, if no error occurs; otherwise rval is set to None and errorstr contains
        appropriate error string. If the LMIShell does not dump exceptions, an appropriate
        exception is raised.

        Raised exceptions:
            LMIFilterError
            CIMError
            AuthError

        Arguments:
            class_name -- string of a class name
            namespace -- string containing the namespace name, where the class lives
            inst_filter -- dictionary containing filter values. The key corresponds to the
                primary key of the CIMInstanceName; value contains the filtering value.

        Keyword Arguments:
            Key, key -- filtering key, see above
            Value, value -- filtering value, see above
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
        Returns a LMIReturnValue object, where rval is set to CIMInstance object, if
        no error occurs; otherwise errorstr is set to corresponding error string. If the
        LMIShell does not dump exceptions, an appropriate exception is raised.

        Raised exceptions:
            CIMError
            AuthError

        Arguments:
            path -- CIMInstanceName object

        Keyword Arguments:
            LocalOnly -- bool flag indicating if to include the only elements (properties,
                methods, references) overridden or defined in the class
            IncludeQualifiers -- bool flag indicating, if all Qualifiers for the class and
                its elements shall be included in the response
            IncludeClassOrigin -- bool flag indicating, if the CLASSORIGIN attribute shall
                be present on all appropriate elements in the returned class
            PropertyList -- if present and not None, the members of the list define one or
                more property names. The returned class shall not include elements for
                properties missing from this list. Note that if LocalOnly is specified as
                True, it acts as an additional filter on the set of properties returned. For
                example, if property A is included in the PropertyList but LocalOnly is set to
                True and A is not local to the requested class, it is not included in the
                response. If the PropertyList input parameter is an empty list, no properties
                are included in the response. If the PropertyList input parameter is None, no
                additional filtering is defined.
        """
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
        Returns LMIReturnValue object with rval set to a list of CIMIntance objects, if no
        error occurs; otherwise rval is set to None and errorstr is set to corresponding
        error string. If the LMIShell does not dump exceptions, an appropriate exception is
        raised.

        Raised exceptions:
            CIMError
            AuthError

        Arguments:
            class_name -- string of a class name
            namespace -- namespace, where the class lives
            inst_filter -- dictionary containing filter values. The key corresponds to the
                primary key of the CIMInstanceName; value contains the filtering value.

        Keyword Arguments:
            Key, key -- filtering key, see above
            Value, value -- filtering value, see above
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
        (inst_list, _, errorstr)  = self._exec_query(LMIBaseClient.QUERY_LANG_WQL, query, namespace)
        if not inst_list:
            return LMIReturnValue(rval=None, errorstr=errorstr)
        return LMIReturnValue(rval=inst_list)

    def _get_class_names(self, namespace=None, **kwargs):
        """
        Returns a LMIReturnValue object with rval set to a list of strings containing
        class names, if no error occurs; otherwise rval is set to None and errorstr
        contains an appropriate error string. If the LMIShell does not dump exceptions, an appropriate
        exception is raised.

        Raised exceptions:
            CIMError
            AuthError

        Arguments:
            namespace -- string containing the namespace, from which the class names list
                should be retreived; if None, default namespace will be used -- see pywbem

        Keyword Arguments:
            ClassName -- defines the class that is the basis for the enumeration. If the
                ClassName input parameter is absent, this implies that the names of all
                classes. Default value is None.
            DeepInheritance -- if not present, of False, only the names of
                immediate child subclasses are returned, otherwise the names of all
                subclasses of the specified class should be returned. Default value is
                False.
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
        Returns a LMIReturnValue object with rval set to a list of CIMClass objects, if no
        error occurs; otherwise rval is set to None and errorstr to appropriate error
        string. If the LMIShell does not dump exceptions, an appropriate exception is raised.

        Raised exceptions:
            CIMError
            AuthError

        Arguments:
            namespace -- string containing the namespace, from which the class names list
                should be retreived; if None, default namespace will be used -- see pywbem

        Keyword Arguments:
            ClassName -- defines the class that is the basis for the enumeration. If the
                ClassName input parameter is absent, this implies that the names of all
                classes. Default value is None.
            DeepInheritance -- if not present, of False, only the names of
                immediate child subclasses are returned, otherwise the names of all
                subclasses of the specified class should be returned. Default value is
                False.
            LocalOnly -- bool flag indicating, if any CIM elements (properties, methods,
                and qualifiers) except those added or overridden in the class as specified in
                the classname input parameter shall not be included in the returned class.
            IncludeQualifiers -- bool flag indicating, if all qualifiers for each class
                (including qualifiers on the class and on any returned properties,
                methods, or method parameters) shall be included as <QUALIFIER> elements
                in the response.
            IncludeClassOrigin -- bool flag indicating, if the CLASSORIGIN attribute shall
                be present on all appropriate elements in each returned class.
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
        Returns a LMIReturnValue object with rval set to CIMClass, if no error occurs;
        otherwise rval is set to None and errorstr to appropriate error string. If the
        LMIShell does not dump exceptions, an appropriate exception is raised.

        Raised exceptions:
            CIMError
            AuthError

        Arguments:
            class_name -- string containing the name of the CIMClass
            namespace -- string containing the namespace, from which the class names list
                should be retreived; if None, default namespace will be used -- see pywbem

        Keyword Arguments:
            LocalOnly -- bool flag indicating, if only local members should be present in
                the returned CIMClass; any CIM elements (properties, methods, and qualifiers),
                except those added or overridden in the class as specified in the classname input
                parameter, shall not be included in the returned class. Default value is
                True.
            IncludeQualifiers -- bool flag indicating, if qualifiers for the class
                (including qualifiers on the class and on any returned properties, methods, or
                method parameters) shall be included in the response. Default value is
                True.
            IncludeClassOrigin -- bool flag indicating, if the CLASSORIGIN attribute shall
                be present on all appropriate elements in the returned class. Default
                value is False.
            PropertyList -- if present and not None, the members of the list define one or
                more property names. The returned class shall not include elements for
                properties missing from this list. Note that if LocalOnly is specified as
                True, it acts as an additional filter on the set of properties returned. For
                example, if property A is included in the PropertyList but LocalOnly is set to
                True and A is not local to the requested class, it is not included in the
                response. If the PropertyList input parameter is an empty list, no properties
                are included in the response. If the PropertyList input parameter is None, no
                additional filtering is defined. Default value is None.
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
        Returns string of a superclass to given class, if such superclass exists,
        None otherwise.

        Raised exceptions:
            CIMError
            AuthError

        Arguments:
            class_name -- string containing the name of CIMClass
            namespace -- string containing the namespace of CIMClass
        """
        (minimal_class, _, _) = LMIBaseClient._get_class(self, class_name, namespace,
            LocalOnly=True, IncludeQualifiers=False, PropertyList=[])
        if not minimal_class:
            return None
        return minimal_class.superclass

    def _call_method_raw(self, instance, method, **params):
        """
        Returns a LMIReturnValue object with rval set to return value of the method call,
        rparams set to returned parameters from the method call, if no error occurs;
        otherwise rval is set to -1 and errorstr to appropriate error string. If the
        LMIShell does not dump exceptions, an appropriate exception is raised.

        Raised exceptions:
            CIMError
            AuthError

        Arguments:
            instance -- CIMInstance object, on which the method will be issued
            method -- string containing a method name

        Keyword Arguments:
            params -- parameters passed to the method call
        """
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
        Returns a LMIReturnValue object with rval set to True, rparams set to returned
        parameters from the method call, if no error occurs; otherwise rval is set to
        False and errorstr to appropriate error string. If the LMIShell does not dump
        exceptions, an appropriate exception is raised.

        Raised exceptions:
            CIMError
            AuthError

        Arguments:
            instance -- CIMInstance object, on which the method will be issued
            method -- string containing a method name

        Keyword Arguments:
            params -- parameters passed to the method call
        """
        (rval, rparams, errorstr) = self._call_method_raw(instance, method, **params)
        return LMIReturnValue(rval=(rval == 0), rparams=rparams, errorstr=errorstr)

    def _get_associator_names(self, instance, **params):
        """
        Returns a list of associated CIMInstanceName objects with an input instance, if no
        error occurs; otherwise en empty list is returned. If the LMIShell does not dump
        exceptions, an appropriate exception is raised.

        Raised exceptions:
            CIMError
            AuthError

        Arguments:
            instance -- CIMInstance object

        Keyword Arguments:
            Arguments:
            AssocClass -- valid CIM association class name. It acts as a filter on the
                returned set of names by mandating that each returned name identify an object
                that shall be associated to the source object through an instance of this
                class or one of its subclasses.
            ResultClass -- valid CIM class name. It acts as a filter on the returned set
                of names by mandating that each returned name identify an object that shall be
                either an instance of this class (or one of its subclasses) or be this class
                (or one of its subclasses).
            Role -- valid property name. It acts as a filter on the returned set of names
                by mandating that each returned name identify an object that shall be
                associated to the source object through an association in which the source
                object plays the specified role. That is, the name of the property in the
                association class that refers to the source object shall match the value of
                this parameter.
            ResultRole -- valid property name. It acts as a filter on the returned set of
                names by mandating that each returned name identify an object that shall be
                associated to the source object through an association in which the named
                returned object plays the specified role.  That is, the name of the property
                in the association class that refers to the returned object shall match the
                value of this parameter.
        """
        try:
            return self._cliconn.AssociatorNames(instance.path, **params)
        except (pywbem.cim_operations.CIMError, pywbem.cim_http.AuthError), e:
            lmi_raise_or_dump_exception(e)
            return []

    def _get_associators(self, instance, **params):
        """
        Returns a list of associated CIMInstance objects with an input instance, if no
        error occurs; otherwise an empty list is returned. If the LMIShell does not dump
        exceptions, an appropriate exception is raised.

        Raised exceptions:
            CIMError
            AuthError

        Arguments:
            instance -- CIMInstance object

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
        try:
            return self._cliconn.Associators(instance.path, **params)
        except (pywbem.cim_operations.CIMError, pywbem.cim_http.AuthError), e:
            lmi_raise_or_dump_exception(e)
            return []

    def _get_reference_names(self, instance, **params):
        """
        Returns a list of association CIMInstanceName objects with an input instance, if
        no error occurs; otherwise an empty list is returned. If the LMIShell does not dump
        exceptions, an appropriate exception is raised.

        Raised exceptions:
            CIMError
            AuthError

        Arguments:
            instance -- CIMInstance object

        Keyword Arguments:
            ResultClass -- valid CIM class name. It acts as a filter on the returned set
                of object names by mandating that each returned Object Name identify an
                instance of this class (or one of its subclasses) or this class (or one of its
                subclasses).
            Role -- valid property name. It acts as a filter on the returned set of object
                names by mandating that each returned object name shall identify an object
                that refers to the target instance through a property with a name that matches
                the value of this parameter.
        """
        try:
            return self._cliconn.ReferenceNames(instance.path, **params)
        except (pywbem.cim_operations.CIMError, pywbem.cim_http.AuthError), e:
            lmi_raise_or_dump_exception(e)
            return []

    def _get_references(self, instance, **params):
        """
        Returns a list of association CIMInstance objects with an input instance, if no
        error occurs; otherwise an empty list is returned. If the LMIShell does not dump
        exceptions, an appropriate exception is raised.

        Raised exceptions:
            CIMError
            AuthError

        Arguments:
            instance -- CIMInstance object

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
        try:
            return self._cliconn.References(instance.path, **params)
        except (pywbem.cim_operations.CIMError, pywbem.cim_http.AuthError), e:
            lmi_raise_or_dump_exception(e)
            return []

    def _create_instance(self, classname, namespace, properties=None, qualifiers=None, property_list=None):
        """
        Returns a new CIMInstance, if no error occurs; otherwise None is returned. If the
        LMIShell does not dump exceptions, an appropriate exception is raised.

        Raised exceptions:
            CIMError
            AuthError

        Arguments:
            classname -- string containing a class name of a new instance
            namespace -- string containing a namespace, where the instance lives
            properties -- dictionary containing a property names and values
            qualifiers -- dictionary containing a qualifier names and values
            property_list -- property list for property filtering, see pywbem.CIMInstance
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

    def _modify_instance(self, instance, **params):
        """
        Modifies a CIMInstance object at CIMOM side. Returns LMIReturnValue object with
        rval set to 0, if no error occurs; otherwise rval is set to -1 and errorstr is set
        to corresponding error string. If the LMIShell does not dump exceptions, an
        appropriate exception is raised.

        Raised exceptions:
            CIMError
            AuthError

        Arguments:
            instance -- CIMInstance object to be modified

        Keyword Arguments:
            IncludeQualifiers -- bool flag indicating, if the qualifiers are modified as
                specified in ModifiedInstance. Default value is True.
            PropertyList -- if not None, the members of the list define one or more
                property names. Only properties specified in the PropertyList are
                modified.  Properties of the ModifiedInstance that are missing from the
                PropertyList are ignored. If the PropertyList is an empty list, no
                properties are modified. If the PropertyList is None, the set of
                properties to be modified consists of those of ModifiedInstance with
                values different from the current values in the instance to be modified.
                Default value is None.
        """
        try:
            self._cliconn.ModifyInstance(instance, **params)
        except pywbem.cim_operations.CIMError, e:
            lmi_raise_or_dump_exception(e)
            return LMIReturnValue(rval=e.args[0], errorstr=e.args[1])
        except pywbem.cim_http.AuthError, e:
            lmi_raise_or_dump_exception(e)
            return LMIReturnValue(rval=-1, errorstr=e.args[0])
        return LMIReturnValue(rval=0)

    def _delete_instance(self, instance, **params):
        """
        Deletes a CIMInstance from the CIMOM side. Returns LMIReturnValue object with
        rval set to 0, if no error occurs; otherwise rval is set to -1 and errorstr is set
        to corresponding error string. If the LMIShell does not dump exceptions, an
        appropriate exception is raised.

        Raised exceptions:
            CIMError
            AuthError

        Arguments:
            instance -- CIMInstance object to be deleted
        """
        try:
            self._cliconn.DeleteInstance(instance, **params)
        except pywbem.cim_operations.CIMError, e:
            lmi_raise_or_dump_exception(e)
            return LMIReturnValue(rval=e.args[0], errorstr=e.args[1])
        except pywbem.cim_http.AuthError, e:
            lmi_raise_or_dump_exception(e)
            return LMIReturnValue(rval=-1, errorstr=e.args[0])
        return LMIReturnValue(rval=0)

    def _exec_query(self, query_lang, query, namespace=None):
        """
        Executes a query and returns a LMIReturnValue object with rval set to list of
        CIMInstance objects, if no error occurs; otherwise rval is set to empty list and
        errorstr is set to corresponding error string. If the LMIShell does not dump
        exceptions, an appropriate exception is raised.

        Raised exceptions:
            CIMError
            AuthError

        Arguments:
            query_lang -- string containing a query language
            query -- string containing the query itself
            namespace -- string of the target namespace for the query
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
        Property returning a string of a user name as a part of provided credentials.
        """
        return self._username

    @property
    def hostname(self):
        """
        Property returning a string of a hostname, where the CIMOM is running.
        """
        return self._hostname
