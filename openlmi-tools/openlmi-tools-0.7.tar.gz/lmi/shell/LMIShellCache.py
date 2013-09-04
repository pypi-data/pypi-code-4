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

class LMIShellCache(object):
    """
    Class representing a LMIShell cache.
    """
    def __init__(self, active=True, classname_list=None, class_dict=None,
            class_superclass_dict=None):
        """
        Constructs a LMIShellCache object.

        Arguments:
            active -- bool flag, if the cache is active
            classname_list -- list of cached class names
            class_dict -- dictionary with cached CIMClass objects, where the key is the class
                name and value is CIMClass object
            class_superclass_dict -- dictionary, where the key is namespace and value is
                dictionary of classname:superclass
        """
        self._classname_list = classname_list
        self._class_dict = class_dict if not class_dict is None else {}
        self._class_superclass_dict = class_superclass_dict if not class_superclass_dict is None else {}
        self._active = active

    def clear(self):
        """
        Clears the cache.
        """
        self._classname_list = None
        self._class_dict = {}
        self._class_superclass_dict = {}

    def get_classes(self):
        """
        Returns the list of cached class names' list.
        """
        return self._classname_list

    def set_classes(self, classname_list):
        """
        Stores a new class names' list.
        """
        self._classname_list = classname_list

    def get_class(self, classname):
        """
        Returns a cached CIMClass object, if proper class name provided, otherwise returns
        None.

        Arguments:
            classname -- string containing a cached class name
        """
        if not classname in self._class_dict:
            return None
        return self._class_dict[classname]

    def add_class(self, cim_class):
        """
        Stores a new CIMClass object into the cache.

        Arguments:
            cim_class -- CIMClass object
        """
        self._class_dict[cim_class.classname] = cim_class

    def has_superclass(self, classname, namespace):
        """
        Returns True, if the cache contains superclass to the given
        class name, False otherwise.

        Arguments:
            classname -- string containing a cached class name
            namespace -- string containing a namespace name
        """
        if not namespace in self._class_superclass_dict:
            return False
        if not classname in self._class_superclass_dict[namespace]:
            return False
        return True

    def get_superclass(self, classname, namespace):
        """
        Returns a cached superclass to the given class name.

        Arguments:
            classname -- string containing a cached class name
            namespace -- string containing a namespace name
        """
        if not self.has_superclass(classname, namespace):
            return None
        return self._class_superclass_dict[namespace][classname]

    def add_superclass(self, classname, superclass, namespace):
        """
        Stores a new pair classname : superclassname into the cache.

        Arguments:
            classname -- string containing a class name
            superclass -- string containing a super class name
            namespace -- string containing a namespace name
        """
        if not namespace in self._class_superclass_dict:
            self._class_superclass_dict[namespace] = {}
        self._class_superclass_dict[namespace][classname] = superclass

    @property
    def active(self):
        """
        Property returning, if the cache is active.
        """
        return self._active

    @active.setter
    def active(self, val):
        """
        Property setter for the property active.
        """
        self._active = val
