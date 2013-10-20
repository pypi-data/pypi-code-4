import types

#===========================================================

def interface(t):
    """Decorates class methods making them raise error if called
    
    Example:
    @interface
    class IStream(object):
        def write(self, data):
            '''writes data to stream'''
        
        def flush(self):
            '''flushes all stream buffers'''
    """

    def _abstract_(*args, **kw):
        raise NotImplementedError("abstract method call")

    for name, val in t.__dict__.iteritems():
        if isinstance(val, types.FunctionType):
            setattr(t, name, _abstract_)
    return t
