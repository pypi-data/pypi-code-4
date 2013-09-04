#! /usr/bin/env python3
"""
Module _TUPLES -- Alternate named tuple implementations
Sub-Package STDLIB.COLL of Package PLIB3
Copyright (C) 2008-2013 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

An alternate ``namedtuple`` implementation that does not
use a template and so is not vulnerable to template
injection attacks, and an enhanced ``typed_namedtuple``
that coerces arguments to specified types.
"""

import sys
from collections import OrderedDict
from itertools import chain
from keyword import iskeyword
from operator import itemgetter

from plib.stdlib.builtins import type_from_name
from plib.stdlib.iters import group_into

__all__ = [
    'namedtuple',
    'typed_namedtuple'
]


def _rename_names(names):
    seen = set()
    for index, name in enumerate(names):
        if (not all(c.isalnum() or c=='_' for c in name)
            or iskeyword(name)
            or not name
            or name[0].isdigit()
            or name.startswith('_')
            or name in seen):
            names[index] = '_{:d}'.format(index)
        seen.add(name)


def _validate_names(names):
    for name in names:
        if not all(c.isalnum() or c=='_' for c in name):
            raise ValueError("Type names and field names can only contain alphanumeric characters and underscores: {!r}".format(name))
        if iskeyword(name):
            raise ValueError("Type names and field names cannot be a keyword: {!r}".format(name))
        if name[0].isdigit():
            raise ValueError("Type names and field names cannot start with a number: {!r}".format(name))


def _check_names(names, rename):
    seen = set()
    for name in names:
        if name.startswith('_') and not rename:
            raise ValueError("Field names cannot start with an underscore: {!r}".format(name))
        if name in seen:
            raise ValueError("Encountered duplicate field name: {!r}".format(name))
        seen.add(name)


def _make_attrs(typename, field_names, rename):
    _validate_names([typename] + field_names)
    _check_names(field_names, rename)
    
    def _make(cls, iterable):
        result = tuple.__new__(cls, iterable)
        if len(result) != len(cls._fields):
            raise TypeError("Expected {:d} arguments, got {:d}".format(len(cls._fields), len(result)))
        return result
    
    _make.__doc__ = "Make a new {typename} object from a sequence or iterable".format(**locals())
    
    def _repr(self):
        """Return a nicely formatted representation string"""
        return '{}({})'.format(
            self.__class__.__name__,
            ', '.join('{}={!r}'.format(*args) for args in zip(self._fields, self))
        )
    
    _repr.__name__ = '__repr__'
    
    def _asdict(self):
        """Return a new OrderedDict which maps field names to their values"""
        return OrderedDict(zip(self._fields, self))
    
    def _replace(self, **kwds):
        result = self._make(map(kwds.pop, self._fields, self))
        if kwds:
            raise ValueError('Got unexpected field names: {!r}'.format(list(kwds)))
        return result
    
    _replace.__doc__ = "Return a new {typename} object replacing specified fields with new values".format(**locals())
    
    def _getnewargs(self):
        """Return self as a plain tuple. Used by copy and pickle."""
        return tuple(self)
    
    _getnewargs.__name__ = '__getnewargs__'
    
    attrs = {
        '__slots__': (),
        '_fields': tuple(field_names),
        '_make': classmethod(_make),
        'from_iterable': classmethod(_make),
        '__repr__': _repr,
        '_asdict': _asdict,
        '__dict__': property(_asdict),
        '_replace': _replace,
        '__getnewargs__': _getnewargs
    }
    
    for i, field_name in enumerate(field_names):
        attrs.update({
            field_name: property(itemgetter(i), doc="Alias for field number {:d}".format(i))
        })
    
    return attrs


def _check_args(cls, args, kwds):
    sentinel = object()
    args = args + tuple(kwds.pop(key, sentinel) for key in cls._fields[len(args):])
    assert sentinel not in args
    assert not kwds
    assert len(args) == len(cls._fields)
    return args


def _make_tuple(typename, attrs, arg_list, _new):
    _doc = '{typename}({arg_list})'.format(**locals())
    
    _new.__name__ = '__new__'
    _new.__doc__ = "Create new instance of {}".format(_doc)
    
    attrs.update({
        '__new__': _new,
        '__doc__': _doc
    })
    
    result = type(tuple)(typename, (tuple,), attrs)
    try:
        result.__module__ = sys._getframe(2).f_globals.get('__name__', '__main__')
    except (AttributeError, ValueError):
        pass
    return result


def namedtuple(typename, field_names, rename=False):
    """Returns a new subclass of tuple with named fields.

    >>> Point = namedtuple('Point', ['x', 'y'])
    >>> Point.__doc__                   # docstring for the new class
    'Point(x, y)'
    >>> p = Point(11, y=22)             # instantiate with positional args or keywords
    >>> p[0] + p[1]                     # indexable like a plain tuple
    33
    >>> x, y = p                        # unpack like a regular tuple
    >>> x, y
    (11, 22)
    >>> p.x + p.y                       # fields also accessable by name
    33
    >>> d = p._asdict()                 # convert to a dictionary
    >>> d['x']
    11
    >>> Point(**d)                      # convert from a dictionary
    Point(x=11, y=22)
    >>> p._replace(x=100)               # like str.replace() but targets named fields
    Point(x=100, y=22)
    >>> Test = namedtuple('if', "ok")
    Traceback (most recent call last):
     ...
    ValueError: Type names and field names cannot be a keyword: 'if'
    >>> Test = namedtuple('Test', "ok if")
    Traceback (most recent call last):
     ...
    ValueError: Type names and field names cannot be a keyword: 'if'
    >>> Test = namedtuple('Test', "ok if", rename=True)
    >>> Test._fields
    ('ok', '_1')
    """
    
    if isinstance(field_names, basestring):
        field_names = field_names.replace(',', ' ').split() # names separated by whitespace and/or commas
    field_names = map(str, field_names)
    if rename:
        _rename_names(field_names)
    
    attrs = _make_attrs(typename, field_names, rename)
    
    arg_list = repr(tuple(field_names)).replace("'", "")[1:-1]
    
    def _new(cls, *args, **kwds):
        args = _check_args(cls, args, kwds)
        return tuple.__new__(cls, args)
    
    return _make_tuple(typename, attrs, arg_list, _new)


def _check_type(obj):
    if isinstance(obj, basestring):
        return type_from_name(obj)
    return obj


def typed_namedtuple(typename, fieldspecs, rename=False):
    """Returns a new subclass of tuple with named, typed fields.
    
    >>> Point = typed_namedtuple('Point', 'x int, y int')
    >>> Point.__doc__        # docstring for the new class
    'Point(x <int>, y <int>)'
    >>> p = Point(11, y=22)  # instantiate with positional args or keywords
    >>> p[0] + p[1]          # indexable like a plain tuple
    33
    >>> x, y = p             # unpack like a regular tuple
    >>> x, y
    (11, 22)
    >>> p.x + p.y            # fields also accessible by name
    33
    >>> d = p._asdict()      # convert to a dictionary
    >>> d['x']
    11
    >>> Point(**d)           # convert from a dictionary
    Point(x=11, y=22)
    >>> p._replace(x=100)    # like str.replace() but targets named fields
    Point(x=100, y=22)
    >>> p = Point(11, '22')  # type conversion done on arguments
    >>> all(isinstance(p[i], int) for i in xrange(len(p)))
    True
    >>> x, y = p
    >>> x, y
    (11, 22)
    >>> p = Point(11, 'x')   # invalid arguments raise exception
    Traceback (most recent call last):
     ...
    ValueError: invalid literal for int() with base 10: 'x'
    >>> Test = typed_namedtuple('if', "ok int")
    Traceback (most recent call last):
     ...
    ValueError: Type names and field names cannot be a keyword: 'if'
    >>> Test = typed_namedtuple('Test', "ok int if int")
    Traceback (most recent call last):
     ...
    ValueError: Type names and field names cannot be a keyword: 'if'
    >>> Test = typed_namedtuple('Test', "ok int if int", rename=True)
    >>> Test._fields
    ('ok', '_1')
    >>> Test._fieldtypes
    (<type 'int'>, <type 'int'>)
    >>> Test._fieldspecs
    (('ok', <type 'int'>), ('_1', <type 'int'>))
    >>> Test = typed_namedtuple('Test', [('f1', int), ('f2', int)])
    >>> Test._fieldspecs
    (('f1', <type 'int'>), ('f2', <type 'int'>))
    >>> Test = typed_namedtuple('Test', ['f1', int, 'f2', int])
    >>> Test._fieldspecs
    (('f1', <type 'int'>), ('f2', <type 'int'>))
    >>> Test = typed_namedtuple('Test', ['f1 int', 'f2 int'])
    >>> Test._fieldspecs
    (('f1', <type 'int'>), ('f2', <type 'int'>))
    """
    
    if isinstance(fieldspecs, basestring):
        # Names and types separated by whitespace and/or commas
        fieldspecs = fieldspecs.replace(',', ' ').split()
    if not isinstance(fieldspecs[0], tuple):
        # Format name, type pairs into tuples
        if ' ' in fieldspecs[0]:
            # It's a list of '<name> <type>' strings
            fieldspecs = list(chain(fieldspec.split(' ', 1) for fieldspec in fieldspecs))
        else:
            # It's a list <name>, <type>, <name>, <type>, ...
            fieldspecs = list(group_into(2, fieldspecs))
    field_names = map(str, [spec[0] for spec in fieldspecs])
    if rename:
        _rename_names(field_names)
    field_types = map(_check_type, [spec[1] for spec in fieldspecs])
    field_specs = zip(field_names, field_types)
    
    attrs = _make_attrs(typename, field_names, rename)
    attrs.update({
        '_fieldtypes': tuple(field_types),
        '_fieldspecs': tuple(field_specs)
    })
    
    arg_list = repr([
        '{} <{}>'.format(fieldname, fieldtype.__name__) for fieldname, fieldtype in field_specs
    ]).replace("'", "")[1:-1]
    
    def _new(cls, *args, **kwds):
        args = _check_args(cls, args, kwds)
        return tuple.__new__(cls, tuple(cls._fieldtypes[i](item) for i, item in enumerate(args)))
    
    return _make_tuple(typename, attrs, arg_list, _new)


if __name__ == '__main__':
    from sys import argv as _argv
    verbose = ('-p' in _argv)
    
    from cPickle import loads, dumps
    
    ### NAMEDTUPLE DEMOS
    
    # verify that instances can be pickled
    Point = namedtuple('Point', 'x, y')
    p = Point(x=10, y=20)
    assert p == loads(dumps(p))
    
    # test and demonstrate ability to override methods
    class Point(namedtuple('Point', 'x y')):
        
        __slots__ = ()
        
        @property
        def hypot(self):
            return (self.x ** 2 + self.y ** 2) ** 0.5
        
        def __str__(self):
            return 'Point: x=%6.3f  y=%6.3f  hypot=%6.3f' % (self.x, self.y, self.hypot)
    
    for p in Point(3, 4), Point(14, 5/7.):
        if verbose:
            print p
    
    class Point(namedtuple('Point', ('x', 'y'))):
        """Point class with optimized _make() and _replace() without error-checking"""
        
        __slots__ = ()
        
        _make = classmethod(tuple.__new__)
        
        def _replace(self, _map=map, **kwds):
            return self._make(_map(kwds.get, ('x', 'y'), self))
    
    _output = Point(11, 22)._replace(x=100)
    if verbose:
        print _output
    
    Point3D = namedtuple('Point3D', Point._fields + ('z',))
    if verbose:
        print Point3D.__doc__
    
    ### TYPED_NAMEDTUPLE DEMOS
    
    # verify that instances can be pickled
    Point = typed_namedtuple('Point', 'x int, y int')
    p = Point(x=10, y=20)
    assert p == loads(dumps(p))
    
    # test and demonstrate ability to override methods
    class Point(typed_namedtuple('Point', 'x float y float')):
        
        __slots__ = ()
        
        @property
        def hypot(self):
            return (self.x ** 2 + self.y ** 2) ** 0.5
        
        def __str__(self):
            return 'Point: x=%6.3f y=%6.3f hypot=%6.3f' % (
                self.x, self.y, self.hypot)
    
    for p in Point(3, 4), Point(14, 5), Point(9. / 7, 6):
        if verbose:
            print p
    
    class Point(typed_namedtuple('Point', (('x', int), ('y', int)))):
        """Point class with optimized _make() and _replace() without error-checking"""
        
        __slots__ = ()
        
        _make = classmethod(tuple.__new__)
        
        def _replace(self, _map=map, **kwds):
            return self._make(_map(kwds.get, ('x', 'y'), self))
    
    _output = Point(11, 22)._replace(x=100)
    if verbose:
        print _output
    
    Point3D = typed_namedtuple('Point3D', Point._fieldspecs + (('z', int),))
    if verbose:
        print Point3D.__doc__
    
    ### DOCTESTS
    
    import doctest
    results = doctest.testmod()
    if verbose:
        TestResults = typed_namedtuple('TestResults', 'failed int attempted int')
        print TestResults(*results)
