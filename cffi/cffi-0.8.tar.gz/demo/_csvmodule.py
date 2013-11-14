__version__ = "1.0.cffi"


class Error(Exception):
    pass

QUOTE_MINIMAL    = 0
QUOTE_ALL        = 1
QUOTE_NONNUMERIC = 2
QUOTE_NONE       = 3


class Dialect(object):
    def __init__(self, dialect=None, delimiter=None,
                 doublequote=None, escapechar=None,
                 lineterminator=None, quotechar=None,
                 quoting=None, skipinitialspace=None,
                 strict=None):
        pass


class reader(object):
    pass


class writer(object):
    pass


_dialects = {}

def register_dialect(name, *args, **kwargs):
    if not isinstance(name, basestring):
        raise TypeError("dialect name must be a string or unicode")
    _dialects[name] = Dialect(*args, **kwargs)

def unregister_dialect(name):
    try:
        del _dialects[name]
    except KeyError:
        raise Error("unknown dialect")

def get_dialect(name):
    try:
        return _dialects[name]
    except KeyError:
        raise Error("unknown dialect")

def list_dialects():
    return _dialects.keys()

def field_size_limit(xxx):
    XXX
