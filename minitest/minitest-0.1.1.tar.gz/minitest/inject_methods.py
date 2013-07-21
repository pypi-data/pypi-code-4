import ctypes
import inspect
import operator

from variables import *


VERSION = '0.1.1'
__all__ = []

def get_dict(object):
    _get_dict = ctypes.pythonapi._PyObject_GetDictPtr
    _get_dict.restype = ctypes.POINTER(ctypes.py_object)
    _get_dict.argtypes = [ctypes.py_object]
    return _get_dict(object).contents.value

def set_method_to_builtin(clazz, method_func, method_name=None):
    method_name = method_name or method_func.func_code.co_name
    get_dict(clazz)[method_name] = method_func

def set_method_to_object(method_func, method_name=None):
    set_method_to_builtin(object, method_func, method_name)

def run_compare(actual, expected = True, func = operator.eq):
    test_case = get_current_test_case()
    test_case.add_assertion()
    if not func(actual, expected):
        # print 'false'
        file_info = inspect.getouterframes(inspect.currentframe())[2]
        test_case.add_failure(actual = actual, expected = expected, 
            file_info = file_info[1]+":"+str(file_info[2]))
        get_current_test_method().set_failed()
    return actual

def must_equal(self, other):
    return run_compare(self, other)

def must_equal_with_func(self, other, func):
    return run_compare(self, other, func)

def must_true(self):
    return run_compare(self)

def must_raise(self, raised_exception):
    if hasattr(self, '__call__'):
        try:
            result = self()
            return run_compare(None, raised_exception)
        except Exception, e:
            return run_compare(type(e), raised_exception)
    else:
        "It must be a function."

def p(self):
    print self
    return self

from pprint import pprint
def pp(self):
    pprint(self)
    return self

def inject_musts_methods():
    [set_method_to_object(func) for name, func 
        in globals().iteritems() 
        if name.startswith('must_')]
    set_method_to_object(p)
    set_method_to_object(pp)


inject_musts_methods()

