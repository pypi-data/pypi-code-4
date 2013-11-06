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
import hashlib
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
        Return a new :py:class:`LMIUseExceptionsHelper` instance, if no shared object is
        present; otherwise an existing instance is returned. By default the
        ``use_exceptions`` flag is set to False.
        """
        if cls._instance is None:
            cls._instance = super(LMIUseExceptionsHelper, cls).__new__(cls)
            cls._instance._use_exceptions = False
        return cls._instance

    @property
    def use_exceptions(self):
        """
        :returns: whether the LMIShell should propagate the exceptions, or throw them away
        :rtype: bool
        """
        return self._use_exceptions

    @use_exceptions.setter
    def use_exceptions(self, use=True):
        """
        Property setter, which modifies the bool flag, which indicates, if the LMIShell
        should propagate the exceptions, or dump them.

        :param bool use: specifies, whether to use exceptions in LMIShell
        """
        self._use_exceptions = use

class LMIPassByRef(object):
    """
    Helper class used for passing a value by reference. It uses the advantage of python,
    where all the dictionaries are passed by reference.

    :param val: value, which will be passed by reference

    Example of usage:

    .. code-block:: python

        by_ref = LMIPassByRef(some_value)
        by_ref.value == some_value
    """
    def __init__(self, val):
        self._val = {0 : val}

    @property
    def value(self):
        """
        :returns: value passed by reference.
        """
        return self._val[0]

    @value.setter
    def value(self, new_val):
        """
        Property setter for the value passed by reference.

        :param new_val: new value, which is passed by reference
        """
        self._val[0] = new_val

def lmi_get_use_exceptions():
    """
    :returns: whether the LMIShell should use the exceptions, or throw them away
    :rtype: bool
    """
    return LMIUseExceptionsHelper().use_exceptions

def lmi_set_use_exceptions(use=True):
    """
    Sets a global flag indicating, if the LMIShell should use the exceptions, or throw
    them away.

    :param bool use: specifies, whether the LMIShell should use the exceptions
    """
    LMIUseExceptionsHelper().use_exceptions = use

def lmi_raise_or_dump_exception(e=None):
    """
    Function which either raises an exception, or throws it away.

    :param Exception e: exception, which will be either raised or thrown away
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

    :param string t: string of CIM type
    :param value: variable to cast
    :param dictionary cast: dictionary with :samp:`type : cast_func`
    :returns: cast value
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

    :param string t: string of CIM type
    :param value: variable to cast
    :returns: cast value in :py:mod:`pywbem` type
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

    :param string t: string of CIM type
    :param value: variable to cast
    :returns: cast value in :py:mod:`python` native type
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
    Helper function, which returns wrapped CIM namespace in :py:class:`LMINamespace`.

    :param LMIConnection conn: connection object
    :param string cim_namespace_name: CIM namespace name
    :returns: wrapped CIM namespace into :py:class:`LMINamespace`
    """
    return LMIObjectFactory().LMINamespace(conn, cim_namespace_name)

def lmi_wrap_cim_class(conn, cim_class_name, cim_namespace_name):
    """
    Helper function, which returns wrapped :py:class:`CIMClass` into LMIClass.

    :param LMIConnection conn: connection object
    :param string cim_class_name: string containing :py:class:`CIMClass` name
    :param string cim_namespace_name: string containing :py:class:`CIMNamespace` name, or
        None, if the namespace is not known
    :returns: wrapped :py:class:`CIMClass` into :py:class:`LMIClass`
    """
    lmi_namespace = None
    if cim_namespace_name:
        lmi_namespace = lmi_wrap_cim_namespace(conn, cim_namespace_name)
    return LMIObjectFactory().LMIClass(conn, lmi_namespace, cim_class_name)

def lmi_wrap_cim_instance(conn, cim_instance, cim_class_name, cim_namespace_name):
    """
    Helper function, which returns wrapped :py:class:`CIMInstance` into
    :py:class:`LMIInstance`.

    :param LMIConnection conn: connection object
    :param CIMInstance cim_instance: :py:class:`CIMInstance` object to be wrapped
    :param string cim_class_name: :py:class:`CIMClass` name
    :param string cim_namespace_name: :py:class:`CIMNamespace` name, or None, if the
        namespace is not known
    :returns: wrapped :py:class:`CIMInstance` into :py:class:`LMIInstance`
    """
    lmi_class = lmi_wrap_cim_class(conn, cim_class_name, cim_namespace_name)
    return LMIObjectFactory().LMIInstance(conn, lmi_class, cim_instance)

def lmi_wrap_cim_instance_name(conn, cim_instance_name):
    """
    Helper function, which returns wrapped :py:class:`CIMInstanceName` into
    :py:class:`LMIInstanceName`.

    :param LMIConnection conn: connection object
    :param CIMInstanceName cim_instance_name: :py:class:`CIMInstanceName` object to be
        wrapped
    :returns: wrapped :py:class:`CIMInstanceName` into :py:class:`LMIInstanceName`
    """
    return LMIObjectFactory().LMIInstanceName(conn, cim_instance_name)

def lmi_wrap_cim_method(conn, cim_method_name, lmi_instance, sync_method):
    """
    Helper function, which returns wrapped :py:class:`CIMMethod` into
    :py:class:`LMIMethod`.

    :param LMIConnection conn: connection object
    :param string cim_method_name: method name
    :param LMIInstance lmi_instance: object, on which the method call will be issued
    :param bool sync_method: flag indicating, if we are trying to perform
        a synchronous method call
    :returns: wrapped :py:class:`CIMMethod` into :py:class:`LMIMethod`
    """
    return LMIObjectFactory().LMIMethod(conn, lmi_instance, cim_method_name, sync_method)

def lmi_transform_to_lmi(conn, value):
    """
    Transforms returned values from a method call into LMI wrapped objects. Returns
    transformed input, where :py:class:`CIMInstance` and :py:class:`CIMInstanceName` are
    wrapped into LMI wrapper classes and primitive types are cast to python native types.

    :param LMIConnection conn: connection object
    :param value: object to be transformed into :py:mod:`python` type from :mod:`pywbem` one
    :returns: transformed py::mod:`pywbem` object into LMIShell one
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
    Function returns True if :samp:`lmi_obj` is an instance of a :samp:`lmi_class`, False
    otherwise. When passed :py:class:`LMIInstance`, :py:class:`LMIInstanceName` as
    :samp:`lmi_obj` and :samp:`lmi_class` is of :py:class:`LMIClass` type, function can
    tell, if such :samp:`lmi_obj` is direct instance of :py:class:`LMIClass`, or it's
    super class.

    If :samp:`lmi_obj` and :samp:`lmi_class` is not instance of mentioned classes, an
    exception will be raised.

    :param lmi_obj: instance of :py:class:`LMIInstance` or :py:class:`LMIInstanceName`
        which is checked, if such instance is instance of the ``lmi_class``
    :param LMIClass lmi_class: instance of :py:class:`LMIClass` object
    :returns: whether **lmi_obj** is instance of **lmi_class**
    :rtype: bool
    :raises: :py:exc:`TypeError`
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
    :returns: script name
    :rtype: string
    """
    return os.path.basename(sys.argv[0])

def lmi_associators(assoc_classes):
    """
    Helper function to speed up associator traversal. Returns a list of tuples, where each
    tuple contains :py:class:`LMIInstance` objects, which are in association.

    :param list assoc_classes: list of :py:class:`LMIClass` objects, for which the
        associations will be returned
    :returns: list of tuples of :py:class:`LMIInstance` objects in association
    """
    def make_key(path):
        path.host = None
        return hashlib.md5(path.classname.lower() + path.namespace.lower() + \
            str({ k.lower() : v for k, v in path.keybindings.iteritems() })).hexdigest()

    result = []

    instances = {}
    for assoc_class in assoc_classes:
        conn = assoc_class._conn
        assoc_class.fetch()

        # Reference properties
        ref_props = [
            ref_prop_name \
            for (ref_prop_name, ref_prop) in assoc_class._cim_class.properties.iteritems() \
                if ref_prop.type == "reference"
        ]

        # Reference class names
        ref_class_names = [
            assoc_class._cim_class.properties[ref_prop].reference_class for ref_prop in ref_props
        ]

        # Get instances, which will be joined as associators
        for ref_class_name in ref_class_names:
            (inst_list, out, err) = conn._client._get_instances(ref_class_name)
            instances.update({ make_key(inst.path) : inst for inst in inst_list })

        # Join associated objects
        (assoc_instance_names, out, err) = conn._client._get_instance_names(assoc_class.classname)
        for assoc in assoc_instance_names:
            ref_list = []
            for ref_prop in ref_props:
                path = assoc[ref_prop]
                # XXX: Some association classes report in key property a class, which its
                # instances do not refer to.
                inst = instances.get(make_key(path), None)
                if inst:
                    ref_list.append(
                        lmi_wrap_cim_instance(conn, inst, inst.classname,
                            inst.path.namespace)
                    )

            if len(ref_list) == len(ref_class_names):
                result.append(tuple(ref_list))

    return result
