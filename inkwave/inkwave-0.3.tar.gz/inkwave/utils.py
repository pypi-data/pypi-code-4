import re
from importlib import import_module

converters = {}

_MODULE_RE = re.compile(r'''
    ^(?P<module>.*)
    (?:\.(?P<item>[a-zA-Z_][a-zA-Z0-9_]+)
      (?P<call>\((?P<args>(.*))\))?
    )$
''', re.VERBOSE)

_ARGS_RE = re.compile(r'''
    ^\s*((?P<name>\w+)\s*=\s*)?
    (?P<value>
        True|False|
        \d+.\d+|
        \d+.|
        \d+|
        \w+|
        [urUR]?(?P<strval>"[^"]*?"|'[^']*')
    )\s*$
''', re.VERBOSE)

_PYTHON_CONSTANTS = {
    'None':  None,
    'True':  True,
    'False': False
}


class Converter:
    regexp = r'(.+)'

    def __init__(self, *args, **kwargs):
        pass

    def to_python(self, v):
        return v

    def to_path(self, v):
        return v


def converter(name):
    def d(cls):
        converters[name] = cls
        return cls
    return d


@converter('default')
@converter('string')
class StringConverter(Converter):
    """
    TODO: implement min/max
    """
    pass


@converter('any')
class AnyConverter(Converter):
    pass


def _pythonize(value):
    if value in _PYTHON_CONSTANTS:
        return _PYTHON_CONSTANTS[value]
    for convert in int, float:
        try:
            return convert(value)
        except ValueError:
            pass
    if value[:1] == value[-1:] and value[0] in '"\'':
        value = value[1:-1]
    return value


def parse_args(s):
    s = s.split(',')
    args = []
    kwargs = {}

    for a in s:
        m = _ARGS_RE.match(a)
        if not m:
            return (), {}
        value = m.group('strval')
        name = m.group('name')
        if value is None:
            value = m.group('value')
        value = _pythonize(value)
        if not name:
            args.append(value)
        else:
            kwargs[name] = value

    return tuple(args), kwargs


def check(d1, d2):
    for k, v in d1.items():
        try:
            if d2[k] != v:
                return False
        except KeyError:
            return False
    return True


def dict_get(d, key):
    for k in key.split('.'):
        d = d[k]
    return d


def dict_set(d, key, value):
    segments = key.split('.')
    segments.reverse()
    while segments:
        k = segments.pop()
        if not segments:
            d[k] = value
        else:
            if k in d:
                d = d[k]
            else:
                d[k] = d = {}


class Result:
    def __init__(self, *args):
        self._result = args

    def get(self):
        return self._result


class Error:
    def __init__(self, exc):
        self._exc = exc

    def get(self):
        raise self._exc


def import_object(path):
    m = _MODULE_RE.match(path)
    if not m:
        raise ValueError('Invalid path {}'.format(path))
    module_name = m.group('module')
    item = m.group('item')
    call = m.group('call')
    args = m.group('args')
    try:
        module = import_module(module_name)
    except ImportError:
        raise ValueError('Cannot import module {}'
                         .format(module_name))

    fn = getattr(module, item, None)
    if fn is None:
        raise ValueError('Cannot find {} in module {}'
                         .format(item, module_name))
    if call:
        if args:
            a, kw = parse_args(args)
            return fn(*a, **kw)
        return fn()
    return fn
