import inspect


def has_no_arg_constructor(cls):
    constructor = cls.__init__
    
    if constructor is object.__init__:
        return True
    
    arg_specs = inspect.getargspec(constructor)
    arg_names = arg_specs[0]
    return len(arg_names) == 1
