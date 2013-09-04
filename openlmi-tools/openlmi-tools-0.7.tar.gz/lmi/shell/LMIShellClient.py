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

from LMIBaseClient import LMIBaseClient
from LMIReturnValue import LMIReturnValue
from LMIShellCache import LMIShellCache

class LMIShellClient(LMIBaseClient):
    """
    Derived class from LMIBaseClient.

    This class overrides few methods due to caching.
    """
    def __init__(self, hostname, username="", password="", **kwargs):
        """
        Constructs a LMIShellClient object.

        Arguments:
            hostname -- uri of the CIMOM
            username -- account, under which, the CIM calls will be performed
            password -- user's password

        Keyword Arguments:
            interactive -- flag indicating, if the LMIShell client is running in the
                interactive mode
            use_cache -- flag indicationg, if the LMIShell client should use cache for
                CIMClass objects. This saves a lot's of communication, if there is
                often the LMIShellClient._get_class_names() or ._get_class() call
                issued.
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
        # Set remaining arguments
        interactive = kwargs.pop("interactive", False)
        use_cache = kwargs.pop("use_cache", True)
        conn_type = kwargs.pop("conn_type", LMIBaseClient.CONN_TYPE_WBEM)
        key_file = kwargs.pop("key_file", None)
        cert_file = kwargs.pop("cert_file", None)
        verify_server_cert = kwargs.pop("verify_server_cert", True)
        if kwargs:
            raise TypeError("__init__() got an unexpected keyword arguments: %s" % ", ".join(kwargs.keys()))

        super(LMIShellClient, self).__init__(hostname, username, password, conn_type=conn_type,
            key_file=key_file, cert_file=cert_file, verify_server_cert=verify_server_cert)
        self._interactive = interactive
        self._cache = LMIShellCache(use_cache)

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
                should be retrieved; if None, default namespace will be used -- see pywbem

        Keyword Arguments:
            ClassName -- defines the class that is the basis for the enumeration. If the
                ClassName input parameter is absent, this implies that the names of all
                classes. Default value is None.
            DeepInheritance -- if not present, of False, only the names of
                immediate child subclasses are returned, otherwise the names of all
                subclasses of the specified class should be returned. Default value is
                False.
        """
        if self._cache.active:
            class_list = self._cache.get_classes()
            if class_list is None:
                (class_list, _, errorstr) = LMIBaseClient._get_class_names(self, namespace, **kwargs)
                if not class_list:
                    return LMIReturnValue(rval=class_list, errorstr=errorstr)
                self._cache.set_classes(class_list)
            return LMIReturnValue(rval=class_list)
        return LMIBaseClient._get_class_names(self, namespace, **kwargs)

    def _get_class(self, class_name, namespace=None, **kwargs):
        """
        Returns a LMIReturnValue object with rval set to CIMClass, if no error occurs;
        otherwise rval is set to None and errorstr to appropriate error string. If the
        LMIShell does not dump exceptions, an appropriate exception is raised.

        Arguments:
            class_name -- string containing the name of the CIMClass
            namespace -- string containing the namespace, from which the class names list
                should be retrieved; if None, default namespace will be used -- see pywbem

        Keyword Arguments:
            LocalOnly -- bool flag indicating, if only local members should be present in
                the returned CIMClass; any CIM elements (properties, methods, and qualifiers),
                except those added or overridden in the class as specified in the classname input
                parameter, shall not be included in the returned class
            IncludeQualifiers -- bool flag indicating, if qualifiers for the class
                (including qualifiers on the class and on any returned properties, methods, or
                method parameters) shall be included in the response
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
        if self._cache.active:
            klass = self._cache.get_class(class_name)
            if klass is None:
                (klass, _, errorstr) = LMIBaseClient._get_class(self, class_name, namespace, **kwargs)
                if not klass:
                    return LMIReturnValue(rval=klass, errorstr=errorstr)
                self._cache.add_class(klass)
                self._cache.add_superclass(klass.classname, klass.superclass, namespace)
            return LMIReturnValue(rval=klass)
        return LMIBaseClient._get_class(self, class_name, namespace, **kwargs)

    def _get_superclass(self, classname, namespace=None):
        """
        Returns string of a superclass to given class, if such superclass exists,
        None otherwise.

        Raised exceptions:
            CIMError
            AuthError

        Arguments:
            classname -- string containing the name of CIMClass
            namespace -- string containing the namespace of CIMClass
        """
        if self._cache.active:
            if self._cache.has_superclass(classname, namespace):
                superclass = self._cache.get_superclass(classname, namespace)
            else:
                superclass = LMIBaseClient._get_superclass(self, classname, namespace)
                self._cache.add_superclass(classname, superclass, namespace)
            return superclass
        return LMIBaseClient._get_superclass(self, classname, namespace)

    @property
    def interactive(self):
        """
        Property returning bool value, if the LMIShell is run in the interactive mode.
        """
        return self._interactive

    @interactive.setter
    def interactive(self, i):
        """
        Property setter for interactive flag.

        Arguments:
            i -- bool flag, if the LMIShell is in interactive mode
        """
        self._interactive = bool(i)

    @property
    def use_cache(self):
        """
        Property returning bool flag, which defines, if the LMIShell should use a cache.
        """
        return self._cache.active

    @use_cache.setter
    def use_cache(self, active):
        """
        Property, which sets a bool flag, which defines, if the LMIShell should use a cache.

        Arguments:
            active -- bool flag, if the cache should be used
        """
        self._cache.active = active
