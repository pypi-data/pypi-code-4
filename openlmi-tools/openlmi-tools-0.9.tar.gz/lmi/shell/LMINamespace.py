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

import LMIExceptions

from LMIBaseObject import LMIWrapperBaseObject
from LMIBaseClient import LMIBaseClient

from LMIUtil import lmi_wrap_cim_namespace
from LMIUtil import lmi_wrap_cim_class
from LMIUtil import lmi_transform_to_lmi

class LMINamespace(LMIWrapperBaseObject):
    """
    LMI class representing CIM namespace.

    :param LMIConnection conn: connection object
    :param string name: namespace name
    """
    def __init__(self, conn, name):
        super(LMINamespace, self).__init__(conn)
        self._name = name

    def __getattr__(self, name):
        """
        Returns a :py:class:`LMIClass` object, but first it fetches the classes list from the
        CIMOM.

        :param string name: class member, class name
        :returns: class member or :py:class:`LMIClass` object
        """
        if name in self.__dict__:
            return self.__dict__[name]
        (class_list, _, _) = self._conn._client._get_class_names(self._name, DeepInheritance=True)
        if name in class_list:
            return lmi_wrap_cim_class(self._conn, name, self.name)
        if '_' in name:
            raise LMIExceptions.LMIClassNotFound(self.name, name)
        raise LMIExceptions.LMINamespaceNotFound(self.name, name)

    def __repr__(self):
        """
        :returns: pretty string for the object
        """
        return "%s(namespace='%s', ...)" % (self.__class__.__name__, self.name)

    def classes(self, filter_key="", exact_match=False):
        """
        Returns a list of class names.

        :param string filter_key: substring of a class name
        :param bool exact_match: tells, if to search for exact match or substring
        :returns: list of class names

        **Usage:** :ref:`namespaces_available_classes`.
        """
        (class_name_list, _, errorstr) = self._conn._client._get_class_names(
            self._name, DeepInheritance=True)
        if not class_name_list:
            return []
        if filter_key:
            if not exact_match:
                filter_lambda = lambda n: n.lower().find(filter_key.lower()) >= 0
            else:
                filter_lambda = lambda n: n.lower() == filter_key.lower()
            class_name_list = filter(filter_lambda, class_name_list)
        return class_name_list

    def print_classes(self, filter_key="", exact_match=False):
        """
        Prints out a list of classes.

        :param string filter_key: substring of a class name
        :param bool exact_match: tells, if to search for exact match, or to search for a
            matching substring

        **Usage:** :ref:`namespaces_available_classes`.
        """
        for c in self.classes(filter_key, exact_match):
            sys.stdout.write("%s\n" % c)

    def cql(self, query):
        """
        Executes a CQL query and returns a list of :py:class:`LMIInstance` objects.

        :param string query: CQL query to execute
        :returns: :py:class:`LMIReturnValue` object with ``rval`` set to a list
            of :py:class:`LMIInstance` objects

        **Usage:** :ref:`namespaces_queries`.
        """
        (inst_list, _, errorstr) = self._conn._client._exec_query(LMIBaseClient.QUERY_LANG_CQL, query, self._name)
        if not inst_list:
            return []
        return lmi_transform_to_lmi(self._conn, inst_list)

    def wql(self, query):
        """
        Executes a WQL query and returns a list of :py:class:`LMIInstance` objects.

        :param string query: WQL query to execute
        :returns: :py:class:`LMIReturnValue` object with ``rval`` set to a list
            of :py:class:`LMIInstance` objects

        **Usage:** :ref:`namespaces_queries`.
        """
        (inst_list, _, errorstr) = self._conn._client._exec_query(LMIBaseClient.QUERY_LANG_WQL, query, self._name)
        if not inst_list:
            return []
        return lmi_transform_to_lmi(self._conn, inst_list)

    @property
    def name(self):
        """
        :returns: namespace name
        :rtype: string
        """
        return self._name

class LMINamespaceRoot(LMINamespace):
    """
    Derived class for *root* namespace. Object of this class is accessible
    from :py:class:`LMIConnection` object as a hierarchy entry.

    :param LMIConnection conn: connection object
    """
    def __init__(self, conn):
        super(LMINamespaceRoot, self).__init__(conn, "root")

    @property
    def cimv2(self):
        """
        :returns: *root/cimv2* namespace
        :rtype: :py:class:`LMINamespace`
        """
        return lmi_wrap_cim_namespace(self._conn, "root/cimv2")

    @property
    def interop(self):
        """
        :returns: *root/interop* namespace
        :rtype: :py:class:`LMINamespace`
        """
        return lmi_wrap_cim_namespace(self._conn, "root/interop")

    @property
    def PG_InterOp(self):
        """
        :returns: *root/PG_InterIp* namespace
        :rtype: :py:class:`LMINamespace`
        """
        return lmi_wrap_cim_namespace(self._conn, "root/PG_InterOp")

    @property
    def PG_Internal(self):
        """
        :returns: *root/PG_Internal* namespace
        :rtype: :py:class:`LMINamespace`
        """
        return lmi_wrap_cim_namespace(self._conn, "root/PG_Internal")

    @property
    def namespaces(self):
        """
        :returns: list of strings with available namespaces

        **Usage:** :ref:`namespaces_available_namespaces`.
        """
        return ["cimv2", "interop", "PG_InterOp", "PG_Internal"]

    def print_namespaces(self):
        """
        Prints out all available namespaces accessible via the namespace `root`.

        **Usage:** :ref:`namespaces_available_namespaces`.
        """
        sys.stdout.write("cimv2\n")
        sys.stdout.write("interop\n")
        sys.stdout.write("PG_InterOp\n")
        sys.stdout.write("PG_Internal\n")
