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
    """
    def __init__(self, conn, name):
        """
        Constructs a LMI namespace object.

        Arguments:
            conn -- LMIConnection object
            name -- name of the namespace
        """
        super(LMINamespace, self).__init__(conn)
        self._name = name

    def __getattr__(self, name):
        """
        Returns a LMIClass object, but first it fetches the classes list from the CIMOM.

        Arguments:
            name -- string containing a class name
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
        Returns a pretty string for the object.
        """
        return "%s(namespace='%s', ...)" % (self.__class__.__name__, self.name)

    def classes(self, filter_key="", exact_match=False):
        """
        Returns a list of strings with the class names.

        Arguments:
            filter_key -- string containing either a part of the class name,
                or the whole classname
            exact_match -- bool flag, if to search for exact match, or to search
                for a matching substring
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

        Arguments:
            filter_key -- string containing either a part of the class name,
                or the whole classname
            exact_match -- bool flag, if to search for exact match, or to search
                for a matching substring
        """
        for c in self.classes(filter_key, exact_match):
            sys.stdout.write("%s\n" % c)

    def cql(self, query):
        """
        Executes a CQL query and returns a LMIReturnValue containing a list of
        LMIInstance objects.

        Arguments:
            query -- string containing a CQL query
        """
        (inst_list, _, errorstr) = self._conn._client._exec_query(LMIBaseClient.QUERY_LANG_CQL, query, self._name)
        if not inst_list:
            return []
        return lmi_transform_to_lmi(self._conn, inst_list)

    def wql(self, query):
        """
        Executes a WQL query and returns a LMIReturnValue containing a list of
        LMIInstance objects.

        Arguments:
            query -- string containing a WQL query
        """
        (inst_list, _, errorstr) = self._conn._client._exec_query(LMIBaseClient.QUERY_LANG_WQL, query, self._name)
        if not inst_list:
            return []
        return lmi_transform_to_lmi(self._conn, inst_list)

    @property
    def name(self):
        """
        Property, which returns a namespace name.
        """
        return self._name

class LMINamespaceRoot(LMINamespace):
    """
    Derived class for "root" namespace. Object of this class is accessible from
    LMIConnection object as a hierarchy entry.
    """
    def __init__(self, client):
        """
        Constructs a object with the name of "root".

        Arguments:
            client -- LMIShellClient object used for CIMOM communication
        """
        super(LMINamespaceRoot, self).__init__(client, "root")

    @property
    def cimv2(self):
        """
        Property, which returns a LMINamespace object for the namespace "root/cimv2".
        """
        return lmi_wrap_cim_namespace(self._conn, "root/cimv2")

    @property
    def interop(self):
        """
        Property, which returns a LMINamespace object for the namespace "root/interop".
        """
        return lmi_wrap_cim_namespace(self._conn, "root/interop")

    @property
    def PG_InterOp(self):
        """
        Property, which returns a LMINamespace object for the namespace "root/PG_InterOp".
        """
        return lmi_wrap_cim_namespace(self._conn, "root/PG_InterOp")

    @property
    def PG_Internal(self):
        """
        Property, which returns a LMINamespace object for the namespace "root/PG_Internal".
        """
        return lmi_wrap_cim_namespace(self._conn, "root/PG_Internal")

    @property
    def namespaces(self):
        """
        Returns a list of strings of all available namespaces accessible via the namespace "root".
        """
        return ["cimv2", "interop", "PG_InterOp", "PG_Internal"]

    def print_namespaces(self):
        """
        Prints out all available namespaces accessible via the namespace "root".
        """
        sys.stdout.write("cimv2\n")
        sys.stdout.write("interop\n")
        sys.stdout.write("PG_InterOp\n")
        sys.stdout.write("PG_Internal\n")
