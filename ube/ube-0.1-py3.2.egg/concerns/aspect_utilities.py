'''
Created on Nov 6, 2012

@author: Nicklas Boerjesson
'''
from inspect import getfullargspec



def alter_function_parameter_and_call(function_object, args, kwargs, name, value, err_if_not_set):
    """changes an argument value of a given function and call said function"""
    argspec = getfullargspec(function_object)

    try:
        arg_idx = argspec.args.index(name)
    except:
        raise Exception(err_if_not_set)
    largs = list(args)
    largs.pop(arg_idx)
    largs.insert(arg_idx, value)
    new_args = tuple(largs)

    return function_object(*new_args, **kwargs)