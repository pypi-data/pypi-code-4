def strip_whitespaces(func):
    '''
    Strip whitespaces from str and unicode arguments
    '''
    def wrapper(*args, **kwargs):
        cleaned_args = []
        for arg in args:
            if isinstance(arg, basestring):
                arg = arg.strip()
            cleaned_args.append(arg)
        return func(*cleaned_args, **kwargs)
    return wrapper