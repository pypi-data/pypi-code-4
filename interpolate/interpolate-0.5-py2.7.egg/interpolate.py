from __future__ import print_function

import __future__
import operator
import string
import sys


_basestring = globals().get('basestring', str)
_future_mask = reduce(operator.or_, [f.compiler_flag for f in [getattr(__future__, k) for k in __future__.all_feature_names]], 0)


class _Formatter(string.Formatter):
    def __init__(self, locals_, globals_, flags=0):
        self.locals = locals_
        self.globals = globals_
        self.flags = flags & _future_mask

    def get_field(self, field_name, args, kwargs):
        if isinstance(field_name, _basestring) and field_name not in kwargs:
            co = compile(field_name, '<eval>', mode='eval', flags=self.flags)
            return (eval(co, self.locals, self.globals), None)
        else:
            return string.Formatter.get_field(self, field_name, args, kwargs)


class _UDict(object):
    def __init__(self, *a):
        self.maps = a

    def __getitem__(self, k):
        m = list(self.maps)
        while m:
            try:
                return m.pop(0)[k]
            except KeyError:
                continue
        raise KeyError(k)

    def __contains__(self, k):
        return any(k in d for d in self.maps)


class _Interpolate(object):
    def interpolate(self, str_):
        frame = sys._getframe(2)
        code = frame.f_code
        args = [frame.f_locals.get(f)
                for f in code.co_varnames[:code.co_argcount]]
        if code.co_flags & 0x04:
            if code.co_flags & 0x08:
                offset = 1
            else:
                offset = 0
            args.extend(frame.f_locals[code.co_varnames[-1 - offset]])
        fmt = _Formatter(frame.f_locals, frame.f_globals, code.co_flags)
        m = _UDict(frame.f_locals, frame.f_globals)
        return fmt.vformat(str_, tuple(args), m)

    def __mod__(self, other):
        if isinstance(other, _basestring):
            return self.interpolate(other)
        else:
            return NotImplemented

    def __call__(self, fmt):
        return self.interpolate(fmt)

i = _Interpolate()
