import ctypes
import inspect
import operator

from variables import *
import types

__all__ = []

def get_dict(obj):
    _get_dict = ctypes.pythonapi._PyObject_GetDictPtr
    _get_dict.restype = ctypes.POINTER(ctypes.py_object)
    _get_dict.argtypes = [ctypes.py_object]
    return _get_dict(obj).contents.value

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

def must_equal(self, other, key=operator.eq):
    return run_compare(self, other, key)

def must_equal_with_func(self, other, func):
    ''' deprecated, now just use must_equal's key parameter '''
    return run_compare(self, other, func)

def must_true(self):
    return run_compare(self)

def must_raise(self, raised_exception, exception_msg=None):
    if hasattr(self, '__call__'):
        try:
            result = self()
            return run_compare(None, raised_exception)
        except Exception, e:
            if type(e) == raised_exception and exception_msg != None:
                return run_compare(str(e), exception_msg)
            else:
                return run_compare(type(e), raised_exception)
    else:
        "It must be a function."

def gen_title_from_stack_info(stack_info):
    ''' it will generate the title from stack info.

    '''
    text  = stack_info[-2][-1]
    index = text.rfind(".")
    return text[:index]+" :"

import traceback
def p(self, title=None, auto_get_title=True):
    result = self
    if type(result) == types.NoneType:
        result = None
    if title:
        print title, result
    else:
        if auto_get_title:
            print gen_title_from_stack_info(
                traceback.extract_stack()), result
        else:
            print result
    return result

from pprint import pprint
def pp(self, title=None, auto_get_title=True):
    result = self
    if type(result) == types.NoneType:
        result = None
    if title:
        print title
    else:
        if auto_get_title:
            print gen_title_from_stack_info(
                traceback.extract_stack())
    pprint(result)
    return result

def length(self):
    return len(self)

def size(self):
    return len(self)

def inject_musts_methods():
    [set_method_to_object(func) for name, func 
        in globals().iteritems() 
        if name.startswith('must_')]
    set_method_to_object(p)
    set_method_to_object(pp)
    set_method_to_object(length)
    set_method_to_object(size)
    # for None
    set_method_to_builtin(types.NoneType, classmethod(p), 'p')
    set_method_to_builtin(types.NoneType, classmethod(pp), 'pp')


inject_musts_methods()

