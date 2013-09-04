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

import os
import sys
import pywbem

from LMIObjectFactory import LMIObjectFactory

# By default, the LMIShell does not use exceptions; LMIReturnValue
# is used instead (with proper error string).
class LMIUseExceptionsHelper(object):
    """
    Singleton helper class used for storing a bool flag, which defines,
    if the LMIShell should propagate exceptions or dump them.
    """
    _instance = None

    def __new__(cls):
        """
        Return a new LMIUseExceptionsHelper instance, if no shared object
        is present; otherwise an existing instance is returned. By default
        the "use_exceptions" flag is set to False.
        """
        if cls._instance is None:
            cls._instance = super(LMIUseExceptionsHelper, cls).__new__(cls)
            cls._instance._use_exceptions = False
        return cls._instance

    @property
    def use_exceptions(self):
        """
        Property returning a bool flag, which indicates, if the LMIShell should
        propagate the exceptions, or dump them.
        """
        return self._use_exceptions

    @use_exceptions.setter
    def use_exceptions(self, use=True):
        """
        Property setter, which modifies the bool flag, which indicates, if the LMIShell
        should propagate the exceptions, or dump them.
        """
        self._use_exceptions = use

class LMIPassByRef(object):
    """
    Helper class used for passing a value by reference. It uses the advantage of python,
    where all the dictionaries are passed by reference.

    Example of usage:
        by_ref = LMIPassByRef(some_value)
        by_ref.value == some_value
    """
    def __init__(self, val):
        """
        Constructs a LMIPassByRef object.

        Arguments:
            val -- value, which will be passed by reference
        """
        self._val = {0 : val}

    @property
    def value(self):
        """
        Property returning the value passed by reference.
        """
        return self._val[0]

    @value.setter
    def value(self, new_val):
        """
        Property setter for the value passed by reference.
        """
        self._val[0] = new_val

def lmi_get_use_exceptions():
    """
    Returns a global flag indicating, if the LMIShell should use the exceptions,
    or dump them.
    """
    return LMIUseExceptionsHelper().use_exceptions

def lmi_set_use_exceptions(use=True):
    """
    Sets a global flag indicating, if the LMIShell should use the exceptions,
    or dump them.
    """
    LMIUseExceptionsHelper().use_exceptions = use

def lmi_raise_or_dump_exception(e=None):
    """
    Function which either raises an exception, or throws it away.
    """
    if not lmi_get_use_exceptions():
        return
    (et, ei, tb) = sys.exc_info()
    if e is None:
        raise et, ei, tb
    else:
        raise type(e), e, tb

def _lmi_do_cast(t, value, cast):
    """
    Helper function, which preforms the actual cast.

    Arguments:
        t -- string of CIM type
        value -- variable to cast
        cast -- dictionary with type:cast_func
    """
    cast_func = cast.get(t.lower(), lambda x: x)
    if isinstance(value, (dict, pywbem.NocaseDict)):
        return pywbem.NocaseDict({
            k: _lmi_do_cast(t, val, cast) for k, val in value.iteritems()})
    elif isinstance(value, list):
        return map(lambda val: _lmi_do_cast(t, val, cast), value)
    elif isinstance(value, tuple):
        return tuple(map(lambda val: _lmi_do_cast(t, val, cast), value))
    return cast_func(value)

def lmi_cast_to_cim(t, value):
    """
    Casts the value to CIM type.

    Arguments:
        t -- string of CIM type
        value -- variable to cast
    """
    cast = {
        "sint8"  : lambda x: pywbem.Sint8(x),
        "uint8"  : lambda x: pywbem.Uint8(x),
        "sint16" : lambda x: pywbem.Sint16(x),
        "uint16" : lambda x: pywbem.Uint16(x),
        "sint32" : lambda x: pywbem.Sint32(x),
        "uint32" : lambda x: pywbem.Uint32(x),
        "sint64" : lambda x: pywbem.Sint64(x),
        "uint64" : lambda x: pywbem.Uint64(x),
        "reference": lambda x: x.path if isinstance(x, LMIObjectFactory().LMIInstance) else x
    }
    return _lmi_do_cast(t, value, cast)

def lmi_cast_to_lmi(t, value):
    """
    Casts the value to LMI (python) type.

    Arguments:
        t -- string of CIM type
        value -- variable to cast
    """
    cast = {
        "sint8"  : lambda x: int(x),
        "uint8"  : lambda x: int(x),
        "sint16" : lambda x: int(x),
        "uint16" : lambda x: int(x),
        "sint32" : lambda x: int(x),
        "uint32" : lambda x: int(x),
        "sint64" : lambda x: int(x),
        "uint64" : lambda x: int(x),
    }
    return _lmi_do_cast(t, value, cast)

def lmi_wrap_cim_namespace(conn, cim_namespace_name):
    """
    Helper function, which returns wrapped CIMNamespace into LMINamespace.

    Arguments:
        conn -- LMIConnection object
        cim_namespace_name -- string containing CIMNamespace name
    """
    return LMIObjectFactory().LMINamespace(conn, cim_namespace_name)

def lmi_wrap_cim_class(conn, cim_class_name, cim_namespace_name):
    """
    Helper function, which returns wrapped CIMClass into LMIClass.

    Arguments:
        conn -- LMIConnection object
        cim_class_name -- string containing CIMClass name
        cim_namespace_name -- string containing CIMNamespace name,
             or None, if the namespace is not known
    """
    lmi_namespace = None
    if cim_namespace_name:
        lmi_namespace = lmi_wrap_cim_namespace(conn, cim_namespace_name)
    return LMIObjectFactory().LMIClass(conn, lmi_namespace, cim_class_name)

def lmi_wrap_cim_instance(conn, cim_instance, cim_class_name, cim_namespace_name):
    """
    Helper function, which returns wrapped CIMInstance into LMIInstance.

    Arguments:
        conn -- LMIConnection object
        cim_instance -- CIMInstance object to be wrapped
        cim_class_name -- string containing CIMClass name
        cim_namespace_name -- string containing CIMNamespace name,
            or None, if the namespace is not known
    """
    lmi_class = lmi_wrap_cim_class(conn, cim_class_name, cim_namespace_name)
    return LMIObjectFactory().LMIInstance(conn, lmi_class, cim_instance)

def lmi_wrap_cim_instance_name(conn, cim_instance_name):
    """
    Helper function, which returns wrapped CIMInstanceName into LMIInstanceName.

    Arguments:
        conn -- LMIConnection object
        cim_instance_name -- CIMInstanceName object to be wrapped
    """
    return LMIObjectFactory().LMIInstanceName(conn, cim_instance_name)

def lmi_wrap_cim_method(conn, cim_method_name, lmi_instance, sync_method):
    """
    Helper function, which returns wrapped CIMMethod imto LMIMethod.

    Arguments:
        conn -- LMIConnection object
        cim_method_name -- string containing a method name
        lmi_instance -- LMIInstance object, on which the method call will be issued
        sync_method -- bool flag indicating, if we are trying to perform
            a synchronous method call
    """
    return LMIObjectFactory().LMIMethod(conn, lmi_instance, cim_method_name, sync_method)

def lmi_transform_to_lmi(conn, value):
    """
    Transforms returned values from a method call into LMI wrapped objects. Returns
    transformed input, where CIMInstance and CIMInstanceName are wrapped into LMI
    wrapper classes and primitive types are cast to python native types.

    Arguments:
        conn -- LMIConnection object
        value -- object to be transformed into python type from pywbem one
    """
    if isinstance(value, pywbem.cim_obj.CIMInstance):
        namespace = value.path.namespace if value.path else None
        return lmi_wrap_cim_instance(conn, value, value.classname, namespace)
    elif isinstance(value, pywbem.cim_obj.CIMInstanceName):
        return lmi_wrap_cim_instance_name(conn, value)
    elif isinstance(value, pywbem.CIMInt):
        return int(value)
    elif isinstance(value, pywbem.CIMFloat):
        return float(value)
    elif isinstance(value, (dict, pywbem.NocaseDict)):
        return pywbem.NocaseDict({
                k: lmi_transform_to_lmi(conn, val)
            for k, val in value.iteritems()})
    elif isinstance(value, list):
        return map(lambda val: lmi_transform_to_lmi(conn, val), value)
    elif isinstance(value, tuple):
        return tuple(map(lambda val: lmi_transform_to_lmi(conn, val), value))
    return value

def lmi_isinstance(lmi_obj, lmi_class):
    """
    Function returns True if lmi_obj is an instance of a lmi_class, False otherwise. When
    passed LMIInstance, LMIInstanceName as lmi_obj and lmi_class is of LMIClass type,
    function can tell, if such lmi_obj is direct instance of LMIClass, or it's super
    class.

    If lmi_obj and lmi_class is not instance of mentioned classes, an exception will be
    raised.

    Raised exceptions:
        TypeError

    Arguments:
        lmi_obj -- LMIInstance or LMIInstanceName
        lmi_class -- LMIClass object
    """
    if not isinstance(lmi_obj, (LMIObjectFactory().LMIInstance,
            LMIObjectFactory().LMIInstanceName)) or \
            not isinstance(lmi_class, LMIObjectFactory().LMIClass):
        errorstr = "Use with types LMIInstance/LMIInstanceName and LMIClass"
        lmi_raise_or_dump_exception(TypeError(errorstr))
        return False
    client = lmi_obj._conn._client
    classname = lmi_obj.classname
    namespace = lmi_obj.namespace
    while classname:
        if classname == lmi_class.classname:
            return True
        classname = client._get_superclass(classname, namespace)
    return False

def lmi_script_name():
    """
    Returns a string of executed script.
    """
    return os.path.basename(sys.argv[0])
