"""
concon (CONstrained CONtainers) provides usefully constrained container
subtypes as well as utilities for defining new constrained subtypes and
append-only dict modification.

There are two flavors of constraints: frozen and appendonly.  The former
prevents any modification and the latter prevents any modification of
an existing entry.  These two flavors of constraint are applied to the
set, list, and dict types.

(Note: frozenset is already a builtin, but is also provided in this
module scope for consistency.)
"""

import unittest
from collections import Mapping


## General Constraint abstractions:

class ConstraintError (TypeError):
    """
    ConstraintError is the base Exception type for any violation of
    some constraint.
    """
    Template = 'Attempt to call %r.%s %r %r violates constraint.'

    def __str__(self):
        return self.Template % self.args

    @classmethod
    def block(cls, method):
        """
        This decorator raises a ConstraintError (or subclass) on any
        call to the given method.
        """
        def blocked_method(self, *a, **kw):
            raise cls(self, method.__name__, a, kw)
        return blocked_method


def define_constrained_subtype(prefix, base, blockednames, clsdict=None):
    """
    Define a subtype which blocks a list of methods.

    @param prefix: The subtype name prefix.  This is prepended to the
                   base type name.  This convention is baked in for
                   API consistency.

    @param base: The base type to derive from.

    @param blockednames: A list of method name strings.  All of these
                         will be blocked.

    @param clsdict: None or a dict which will be modified to become the
                    subtype class dict.

    @return: The new subtype.

    @raise: OverwriteError - If clsdict contains an entry in blockednames.
    """
    name = prefix + base.__name__

    clsdict = clsdict or {}

    doc = clsdict.get('__doc__', '')
    doc = 'An %s extension of %s.\n%s' % (prefix, base.__name__, doc)
    clsdict['__doc__'] = doc

    setitem_without_overwrite(clsdict, 'get_blocked_method_names', lambda self: iter(blockednames))

    for bname in blockednames:
        setitem_without_overwrite(clsdict, bname, ConstraintError.block(getattr(base, bname)))

    return type(name, (base,), clsdict)


## Overwrite utilities:

class OverwriteError (ConstraintError, KeyError):
    """
    OverwriteError is raised when an attempt to overwrite a value in an
    append-only structure occurs.
    """

    Template = 'Attempted overwrite of key %r with new value %r overwriting old value %r'

    def __init__(self, key, newvalue, oldvalue):
        KeyError.__init__(self, key, newvalue, oldvalue)


def setitem_without_overwrite(d, key, value):
    """
    @param d: An instance of dict, that is: isinstance(d, dict)
    @param key: a key
    @param value: a value to associate with the key

    @return: None

    @raise: OverwriteError if the key is already present in d.
    """
    if key in d:
        raise OverwriteError(key, value, d[key])
    else:
        dict.__setitem__(d, key, value)


def update_without_overwrite(d, *args, **kwds):
    """
    This has the same interface as dict.update except it uses
    setitem_without_overwrite for all updates.

    Note: The implementation is derived from
    collections.MutableMapping.update.
    """
    if args:
        assert len(args) == 1, 'At most one positional parameter is allowed: {0!r}'.format(args)
        (other,) = args
        if isinstance(other, Mapping):
            for key in other:
                setitem_without_overwrite(d, key, other[key])
        elif hasattr(other, "keys"):
            for key in other.keys():
                setitem_without_overwrite(d, key, other[key])
        else:
            for key, value in other:
                setitem_without_overwrite(d, key, value)

    for key, value in kwds.items():
        setitem_without_overwrite(d, key, value)


## Concrete Constrained Containers:

frozenset = frozenset # Promote this builtin to module scope for consistency.

frozenlist = define_constrained_subtype(
    'frozen', list,
    ['__delitem__', '__delslice__', '__iadd__', '__imul__', '__setitem__',
     '__setslice__', 'append', 'extend', 'insert', 'pop', 'remove',
     'reverse', 'sort'])

frozendict = define_constrained_subtype(
    'frozen', dict,
    ['__delitem__', '__setitem__', 'clear', 'pop', 'popitem',
     'setdefault', 'update'])

appendonlyset = define_constrained_subtype(
    'appendonly', set,
    ['__iand__', '__isub__', '__ixor__', 'clear', 'difference_update',
     'discard', 'intersection_update', 'pop', 'remove',
     'symmetric_difference_update'])

appendonlylist = define_constrained_subtype(
    'appendonly', list,
    ['__setitem__', '__delitem__', 'insert', 'reverse', 'pop', 'remove'])

appendonlydict = define_constrained_subtype(
    'appendonly', dict,
    ['__delitem__', 'pop', 'popitem', 'clear'],
    {'__setitem__': setitem_without_overwrite,
     'update': update_without_overwrite})



## Unittests

class SetItemWithoutOverwriteTests (unittest.TestCase):

    def test__setitem_without_overwrite__no_overwrite(self):
        d = {'a': 'apple'}
        setitem_without_overwrite(d, 'b', 'banana')
        self.assertEqual(d, {'a': 'apple', 'b': 'banana'})

    def test__setitem_without_overwrite__with_overwrite(self):
        d = {'a': 'apple'}
        self.assertRaises(OverwriteError, setitem_without_overwrite, d, 'a', 'applause')

    def test__update_without_overwrite__no_overwrite(self):
        d = {'a': 'apple'}
        update_without_overwrite(d, {'b': 'banana'})
        self.assertEqual(d, {'a': 'apple', 'b': 'banana'})

    def test__update_without_overwrite__with_overwrite(self):
        d = {'a': 'apple'}
        self.assertRaises(OverwriteError, update_without_overwrite, d, {'a': 'applause'})

    def test__update_without_overwrite__with_NonMappingWithKeysAndGetItem(self):
        class NonMappingWithKeysAndGetItem (object):
            def keys(self):
                return ['a', 'b', 'c']
            def __getitem__(self, key):
                return 42

        d = {}
        update_without_overwrite(d, NonMappingWithKeysAndGetItem())
        self.assertEqual(d, {'a': 42, 'b': 42, 'c': 42})

    def test__update_without_overwrite__with_keyvalue_sequence(self):
        d = {}
        update_without_overwrite(d, [('a', 0), ('b', 1), ('c', 2)])
        self.assertEqual(d, {'a': 0, 'b': 1, 'c': 2})

    def test__update_without_overwrite__with_keywords(self):
        d = {}
        update_without_overwrite(d, a=0, b=1, c=2)
        self.assertEqual(d, {'a': 0, 'b': 1, 'c': 2})


class BlockedMethodsTests (unittest.TestCase):

    def test_frozendict(self):
        self._check_blocked_methods(frozendict({}))

    def test_frozenlist(self):
        self._check_blocked_methods(frozenlist({}))

    # Note, we do not test frozenset.

    def test_appendonlydict(self):
        self._check_blocked_methods(appendonlydict({}))

    def test_appendonlylist(self):
        self._check_blocked_methods(appendonlylist({}))

    def test_appendonlyset(self):
        self._check_blocked_methods(appendonlyset({}))

    def _check_blocked_methods(self, obj):
        for name in obj.get_blocked_method_names():
            method = getattr(obj, name)
            self.assertRaises(ConstraintError, method, 42)


class ContraintErrorTests (unittest.TestCase):

    def test___str__(self):
        error = ConstraintError(None, 'foo', ('blah', 42), dict(wombat='awesome!'))
        self.assertRegexpMatches(str(error), r'^Attempt to call .* violates constraint\.$')




if __name__ == '__main__':
    unittest.main()
