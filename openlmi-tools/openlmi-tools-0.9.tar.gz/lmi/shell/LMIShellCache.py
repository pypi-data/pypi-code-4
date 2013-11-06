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

    :param bool active: specifies, if the cache is active
    :param list classname_list: list of strings of cached class names
    :param dictionary class_dict: cached :py:class:`CIMClass` objects, where the key is
        the class name and value is :class:`CIMClass` object
    :param dictionary class_superclass_dict: dictionary, where the key is namespace and
        value is dictionary of classname:superclass
    """
    def __init__(self, active=True, classname_list=None, class_dict=None,
            class_superclass_dict=None):
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
        :returns: list of cached class names
        """
        return self._classname_list

    def set_classes(self, classname_list):
        """
        Stores a new class names' list.
        """
        self._classname_list = classname_list

    def get_class(self, classname):
        """
        :param string classname: cached class name
        :returns: cached :py:class:`CIMClass` object, if proper class name provided, None otherwise
        """
        if not classname in self._class_dict:
            return None
        return self._class_dict[classname]

    def add_class(self, cim_class):
        """
        Stores a new :py:class:`CIMClass` object into the cache.

        :param CIMClass cim_class: :py:class:`CIMClass` object
        """
        self._class_dict[cim_class.classname] = cim_class

    def has_superclass(self, classname, namespace):
        """
        :param string classname: cached class name
        :param string namespace: namespace name
        :returns: True, if the cache contains superclass to the given class name; False otherwise
        """
        if not namespace in self._class_superclass_dict:
            return False
        if not classname in self._class_superclass_dict[namespace]:
            return False
        return True

    def get_superclass(self, classname, namespace):
        """
        :param string classname: cached class name
        :param string namespace: namespace name
        :returns: cached superclass to the given class name
        :rtype: string
        """
        if not self.has_superclass(classname, namespace):
            return None
        return self._class_superclass_dict[namespace][classname]

    def add_superclass(self, classname, superclass, namespace):
        """
        Stores a new pair classname : superclassname into the cache.

        :param string classname: class name to be stored
        :param string superclass: super class name to be stored
        :param string namespace: namespace name of the classname
        """
        if not namespace in self._class_superclass_dict:
            self._class_superclass_dict[namespace] = {}
        self._class_superclass_dict[namespace][classname] = superclass

    @property
    def active(self):
        """
        :returns: True, if the cache is active; False otherwise
        """
        return self._active

    @active.setter
    def active(self, val):
        """
        Property setter for the property active.
        """
        self._active = val
