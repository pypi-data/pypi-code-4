import os
import re
from inkwave.errors import RouteNotFound
from inkwave.utils import (
    converters,
    parse_args,
)


_STATIC = 1
_REGEXP = 2

_PATH_RE = re.compile(r'''
    <
    (?P<variable>[a-zA-Z_][a-zA-Z0-9_]+)
    (?:
      \|                                     # apply converter
      (?P<converter>[a-zA-Z_][a-zA-Z0-9_]*)  # converter name
      (?:\((?P<args>.*?)\))?                 # converter arguments
    )?
    >
''', re.VERBOSE)


def build_path(path):
    used = set()
    pos = 0
    end = len(path)
    search = _PATH_RE.search
    while pos < end:
        m = search(path, pos)
        if m is None:
            remaining = path[pos:]
            if '>' in remaining or '<' in remaining:
                raise ValueError('Invalid path: {}'.format(path))
            yield None, None, remaining
            break
        else:
            variable = m.group('variable')
            converter_name = m.group('converter') or 'default'
            converter_args = m.group('args') or ''
            if m.start() != pos:
                static = path[pos:m.start()]
                yield None, None, static
            if variable in used:
                raise ValueError('Invalid path, variable name {} used'
                                 ' twice'.format(variable))
            try:
                converter_cls = converters[converter_name]
            except KeyError:
                raise ValueError("Invalid path, converter {} isn't"
                                 " registered".format(converter_name))
            a, kw = parse_args(converter_args)
            converter = converter_cls(*a, **kw)
            used.add(variable)
            yield variable, converter, None
            pos = m.end()


class Route:
    def __init__(self, path):
        self.path = path
        regexp = []
        reverse = []
        args = []

        for variable, converter, static in build_path(path):
            if static:
                regexp.append(re.escape(static))
                reverse.append(static)
            else:
                args.append((variable, converter))
                regexp.append(converter.regexp)
                reverse.append('{}')

        self._regexp = re.compile('^' + ''.join(regexp) + '$')
        self._reverse = ''.join(reverse)
        self._args = args

    def match(self, path):
        match = self._regexp.match(path)
        if not match:
            return None

        result = {}
        for (name, conv), value in zip(self._args, match.groups()):
            result[name] = conv.to_python(value)
        return result

    def build_path(self, *args, **kwargs):
        data = []
        args = list(args)
        args.reverse()
        for k, v in self._args:
            arg = args.pop() if args else kwargs[k]
            data.append(v.to_path(arg))
        return self._reverse.format(*data)


class Glob(Route):
    def __init__(self, path):
        self.path = path
        regexp = []
        segments = []
        reverse = []
        args = []

        for s in path.split(os.path.sep):
            if not s:
                continue
            current_segment = []
            current_reverse = []
            segment_type = _STATIC
            for variable, converter, static in build_path(s):
                if static:
                    regexp.append(re.escape(static))
                    current_segment.append((_STATIC, static))
                    current_reverse.append(static)
                else:
                    segment_type = _REGEXP
                    var_re = converter.regexp
                    regexp.append(var_re)
                    current_segment.append((_REGEXP, var_re))
                    current_reverse.append('{}')
                    args.append((variable, converter))

            if segment_type == _STATIC:
                current_segment = ''.join([s for t, s in current_segment])
            else:
                _cseg = [re.escape(s) if t == _STATIC else s
                         for t, s in current_segment]
                current_segment = re.compile(''.join(_cseg))

            segments.append((segment_type, current_segment))
            reverse.append(''.join(current_reverse))

        self._regexp = re.compile('^' + ''.join(regexp) + '$')
        self._segments = segments
        self._reverse = os.path.sep.join(reverse)
        self._args = args

    def _find(self, prefix, segments, args, data={}):
        cwd = prefix
        dynamic = False
        while segments and not dynamic:
            t, s = segments.pop()
            if t == _STATIC:
                cwd = os.path.join(cwd, s)
            else:
                dynamic = True
        if dynamic:
            if not os.path.isdir(cwd):
                raise StopIteration
            for f in os.listdir(cwd):
                match = re.match(s, f)
                if match:
                    full_path = os.path.join(cwd, f)
                    if segments:
                        if not os.path.isdir(full_path):
                            continue

                    data_copy = data.copy()
                    args_copy = args.copy()
                    pop = 0
                    for (name, conv), value in zip(args_copy, match.groups()):
                        pop += 1
                        data_copy[name] = value
                    args_copy = args_copy[pop:]

                    if segments:
                        if os.path.isdir(full_path):
                            yield from self._find(full_path,
                                                  segments.copy(),
                                                  args_copy,
                                                  data_copy)
                    else:
                        yield full_path, data_copy
        else:
            if os.path.exists(cwd):
                yield cwd, data

    def find(self, prefix=''):
        segments = self._segments.copy()
        segments.reverse()
        yield from self._find(prefix, segments, self._args)


class Router:
    def __init__(self):
        self.routes = []
        self._routes_by_name = {}

    def add(self, route, name=None):
        self.routes.append(route)
        if name:
            self._routes_by_name[name] = route

    def dispatch(self, cmd, path, *args, **kwargs):
        for r in self.routes:
            m = r.match(path)
            if m is not None:
                return getattr(r, cmd)(path, m, *args, **kwargs)
        raise RouteNotFound(path)

    def __getitem__(self, key):
        return self._routes_by_name[key]
