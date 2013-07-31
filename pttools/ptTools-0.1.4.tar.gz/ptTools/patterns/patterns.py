#!/usr/bin/env python3

"""Module providing pattern classes for matching against tuples."""

__all__ = [
    'more',
    '_',
    'AnyPattern',
    'ConsPattern',
    'LiteralPattern',
    'TestPattern',
    'TuplePattern',    
    'UnionPattern',
    ]

from ptTools.misc import acceptors
from .. parsetree import tupletraversal


def if_absent_add(set, obj):
    """Adds object to set.  Returns False if element was already
    present, else True."""
    if obj in set:
        return False
    else:
        set.add(obj)
        return True    


class AbstractPattern(object):

    """Abstract superclass for patterns to match against objects."""

    def __or__(self, other):
        """| is a shorthand operator for UnionPattern(A, B).

        Example:
        >>> X = LiteralPattern('x')
        >>> Y = LiteralPattern('y')
        >>> (X | Y).matches('x')
        True
        >>> (X | Y).matches('y')
        True
        
        """
        if isinstance(other, self.union_class):
            return other.__or__(self)
        else:
            return self.union_class(self, other)

    def __pos__(self):
        return PositiveClosurePattern(super().__pos__())

    def __neg__(self):
        return OptionPattern(super().__neg__())

    def __invert__(self):
        return KleeneClosurePattern(super().__invert__())

    def __rshift__(self, other):
        """>> is the operator to create a ConsPattern.

        (A >> B) is a pattern that matches (A (. (. (. B)))) to an
        arbitrary depth of nesting.

        Example:
        >>> X = LiteralPattern('x')
        >>> Y = LiteralPattern('y')
        >>> TuplePattern(X >> Y).matches(('x', (1, (2, (3, 'y')))))
        True

        """
        return ConsPattern(self, RestPattern(self.create_pattern(other)))

    def __repr__(self):
        return self._repr(set())

    @property
    def union_class(self):
        return UnionPattern

    @property
    def final_class(self):
        return FinalPattern

    @property
    def literal_pattern_class(self):
        return LiteralPattern

    @property
    def tuple_pattern_class(self):
        return TuplePattern

    def _repr(self, ignore):
        self._subclass_responsibility()

    def concatenate(self, *args):
        """Returns PatternObject, which is the concatenation of *args."""
        if not args:
            return self.final_class()
        else:
            patterns = [self.create_pattern(obj) for obj in args]
            prev = patterns[0]
            for p in patterns[1:]:
                prev += p
            return prev

    def create_pattern(self, arg): 
        """Creates Pattern object from argument."""
        if isinstance(arg, AbstractPattern):
            return arg
        elif isinstance(arg, tuple):
            return self.tuple_pattern_class(*arg)
        elif isinstance(arg, list):
            if arg:
                ## list translates to regular option.
                return self.concatenate(*arg).__neg__()
            else:
                raise AttributeError('Option cannot be empty')
        else:
            return self.literal_pattern_class(arg) 

    def first_match_in(self, node):
        """Returns first mach in the given branch or None."""
        for n in tupletraversal.preorder(node):
            if self.matches(n):
                return n
        return None

    def match(self, obj):
        """Tries to match given object, applying callbacks if
        matching.  Returns None."""
        self.matches(obj)
        return None

    def matches(self, obj):
        """True, if self matches given tuple or literal object.
        Applies callback functions if successful."""
        ## Must wrap obj into collection, because all
        ## Patterns(acceptors) demand an iterable word.
        path = self.path_of((obj,))
        if not path:
            return False
        elif not path[-1][0].isfinal():
            return False
        else:
            for pattern,arg in path:
                for fn in pattern.callbacks:
                    fn(arg)
            return True
    
    def matches_in(self, node):
        """True if self matches somewhere in the given branch."""
        return any((self.matches(n) for n in tupletraversal.preorder(node)))


    def _repr(self, recur):
        if if_absent_add(recur, self):
            tail = self.successor._repr(recur)
            tail = ', '+tail if tail else tail
            return '{}{}'.format(self._repr_inner(recur), tail)
        else:
            return ''


class AbstractCallbacklessPattern(AbstractPattern):

    @property
    def callbacks(self):
        return ()
    

class AbstractCallbackPattern(AbstractPattern): 

    def __init__(self, *args, callbacks=None, **kwargs):
        """where callbacks is a collection of tuples of (function,
        argument)."""
        self.callbacks = callbacks if callbacks else []
        super().__init__(*args, **kwargs) 

    def __mod__(self, fn):
        """% is the operator to add callback functions to patterns.        

        Returns a new instance (a shallow copy of self) and appends
        the received callback function to the new instance's
        callbacks.  The received function takes whatever self matches
        as its only argument.  fn is called if and only if self
        matched input, and the entire pattern, which is containing
        self, also matched.

        The following example creates patterns with different
        callbacks from the same original pattern.

        >>> X = LiteralPattern('x')
        >>> c1 = []
        >>> c2 = []
        >>> p1 = X%c1.append
        >>> p2 = X%c2.append
        >>> X.matches('x')
        True
        >>> c1 == c2 == []
        True
        >>> p1.matches('x')
        True
        >>> c1
        ['x']
        >>> c2
        []
        
        """
        pattern = self.copy()
        pattern.callbacks.append(fn)
        return pattern

    def _copy_attributes_into(self, copy, dict, *args, **kwargs):
        """Adds aliases to callback functions to shallow copy of self."""
        kwargs['callbacks'] = self.callbacks
        super()._copy_attributes_into(copy, dict, *args, **kwargs)


class FinalPattern(AbstractCallbacklessPattern, acceptors.Final):

    def _repr(self, ignore):
        return ''


class TestPattern(AbstractCallbackPattern, acceptors.Test):

    """Pattern for matching input by calling a given function.

    Example:
    >>> import re
    >>> foomatcher = TestPattern(re.compile('f..').match)
    >>> foomatcher.matches('foo')
    True
    
    """

    def _repr_inner(self, ignore):
        """Returns print string."""
        return str(self.fn)

    def _test(self, obj):
        """True, if self's test function evaluates to True for obj."""
        return self.fn(obj)    


class AnyPattern(AbstractCallbackPattern, acceptors.Test):

    """Pattern, matching any object.

    Example:
    >>> ne = AnyPattern()
    >>> ne.matches('foobar')
    True
    >>> ne.matches((1, (2, 'x')))
    True
    
    """

    def __init__(self, **kwargs):
        kwargs.setdefault('fn', lambda x : True)
        super().__init__(**kwargs)

    def _repr_inner(self, recur):
        return '_'


class LiteralPattern(AbstractCallbackPattern, acceptors.Single):

    """Pattern matching the object it was instantiated with.

    Example:
    >>> X = LiteralPattern('x')
    >>> X.matches('x')
    True

    """

    def _repr_inner(self, recur):
        if isinstance(self.value, str):            
            return "'{}'".format(self.value)
        else:
            return '{}'.format(self.value)

    def _test(self, arg):
        """True, if argument is equal to self.value.  Uses arg.__eq__."""
        ## Using arg.__eq__ instead of value.__eq__ to leave control
        ## at caller.
        return arg == self.value


class TuplePattern(AbstractCallbackPattern, acceptors.AbstractSingle):

    """Class for tuple-like patterns.

    Example:
    >>> p = TuplePattern('a', 23, False)
    >>> p.matches(('a', 23, False))
    True
    
    """

    def __init__(self, *coll, inner=None, **kwargs):
        """Instantiated with zero or more arguments.

        Creates inner pattern, if matches continues with successor.

        """
        if inner:
            self.inner = inner
        elif coll:
            patterns = [self.create_pattern(obj) for obj in coll]
            prev = patterns[0]
            for p in patterns[1:]:
                prev += p
            self.inner = prev
        else:
            self.inner = self.final_class()
        super().__init__(**kwargs)

    def __iter__(self):
        input('foo')

    def _copy_attributes_into(self, copy, dict, *args, **kwargs):
        kwargs['inner'] = self.inner._copy(dict)
        super()._copy_attributes_into(copy, dict, *args, **kwargs)

    def _do(self, fn, recur):
        """Applies fn to all automata in self."""
        if super()._do(fn, recur):
            self.inner._do(fn, recur)

    def _path_of(self, word, path):
        if not word:
            return False
        if not isinstance(word[0], tuple):
            return False
        temp = []
        if not self.inner._path_of(word[0], temp):
            return False
        else:
            assert(isinstance(word[0], tuple))            
            path.append((self, word[0])) ## preorder
            path.extend(temp)
            return self.successor._path_of(word[1:], path)

    def _repr_inner(self, recur):
        return '({})'.format(self.inner._repr(recur))

                 
class UnionPattern(AbstractCallbacklessPattern, acceptors.Union):

    """Class for tuple-like patterns matching any option in tuple.

    Matches the first available option, and disregards the other.

        ## UnionPattern cannot take own callbacks, because the length
        ## of the matched word is unknown.

    Example:
    >>> u = UnionPattern('a', 'b')
    >>> u.matches('a')
    True
    >>> u.matches('b')
    True
    >>> u = UnionPattern(AnyPattern(), AnyPattern()%(lambda void : 1/0))
    >>> u.matches((1, 2, ('foo')))
    True
    
    """
    ## TODO - Implement flags for different modes to handle ambiguous
    ## options.  E.g. a strict mode which raises Error, a warning mode
    ## which outputs warnings only, and a quiet, ambiguity tolerant
    ## mode.

    def __init__(self, *options, **kwargs):
        args = [self.create_pattern(o) for o in options]
        super().__init__(*args, **kwargs)        

    def __mod__(self, fn):
        """% is the operator to add callback functions to patterns.        

        Returns a new instance (a shallow copy of self) and appends
        the received callback function to each of self's options.  The
        received function takes whatever that option matches as its
        only argument.

        """
        copy = self.copy()
        for idx,option in enumerate(copy.options):
            copy.options[idx] = option.__mod__(fn)
        return copy

    def _repr(self, recur):
        ## Need not add to recur, because other, patterns (Nested,
        ## Lit, Tup,..)  will always be traversed before.
        ## TODO - criteria should be if s._repr(recur) returns '' or not
        joined = ''
        for option in self.options:
            child = option._repr(recur)
            if child:
                joined += child + '|'
        return joined.rstrip('|')
        ##return '|'.join((s._repr(recur) for s in self.options if not s.isfinal()))


class NestedPattern(AbstractCallbackPattern, acceptors.Compound):

    def __mod__(self, fn):
        """Adds fn as callback to inner PatternObject."""
        copy_dict = {self.inner : self.inner.__mod__(fn)}
        return self._copy(copy_dict)

    def _repr(self, recur):
        ## TODO - This does not properly embed the inner compound
        ## automaton, because compound does not distinguish between
        ## successor and inner.
        if if_absent_add(recur, self):
            return self.opstr+'('+self.inner._repr(recur)+')'
        else:
            return ''

    def matches(self, ignore):
        """Raises AttributeError."""
        msg = '{} must be nested.'.format(self.__class__.__name__)
        raise AttributeError(msg)


class OptionPattern(NestedPattern):

    def _repr(self, recur):
        if if_absent_add(recur, self):
            return '[ ' + self.inner._repr(recur) + ' ]'
        else:
            return ''


class PositiveClosurePattern(NestedPattern):

    opstr = '+'


class KleeneClosurePattern(NestedPattern):

    opstr = '~'

    
class ConcatenationPattern(NestedPattern):

    opstr = ''
    
    def __init__(self, *args, inner=None, **kwargs):
        if inner:
            kwargs.setdefault('inner', inner)
            assert(not bool(args)) ## kwarg is only used internally,
                                   ## when copying.
        else:
            kwargs.setdefault('inner', self.concatenate(*args))
        super().__init__(**kwargs)

    def __iter__(self):
        input('foo')

    def __mod__(self, ignore):
        """Raises AttributeError, because ConcatenationPattern does
        not match tuple or single input."""        
        raise AttributeError('ConcatenationPattern cannot take callbacks.')        


class ConsPattern(AbstractCallbacklessPattern, acceptors.AbstractSingle):

    """Pattern to match nested children (grandchildren) in trees.

    ConsPattern ::= (first RestPattern)
    RestPattern ::= rest | (any RestPattern)

    Assumes tuple to be of the following form:
    tree ::= (val, (tree | val)*)
    val ::= LITERAL

    Example:
    >>> A = LiteralPattern('a')
    >>> B = LiteralPattern('b')
    >>> P = TuplePattern(A >> B)
    >>> P.matches(('a', (1, (2, (3, 'b')))))
    True
    >>> P.matches(('a', 'b'))
    True
    
    """

    def __init__(self, head, tail, **kwargs):
        """Takes two patterns, of which head has to match immediately,
        and tail, may be nested."""
        self.head = head
        self.tail = tail
        super().__init__(**kwargs)

    def _repr(self, recur):
        ## Need not add to recur, because other, patterns (Nested,
        ## Lit, Tup,..)  will always be traversed before.
        return '{}, {}'.format(self.head._repr(recur), self.tail._repr(recur))

    def _copy_attributes_into(self, copy, dict, **kwargs):
        kwargs['head'] = self.head._copy(dict)
        kwargs['tail'] = self.tail._copy(dict)
        super()._copy_attributes_into(copy, dict, **kwargs)
        
    def _path_of(self, word, path):
        """True, if matches word.  Appends tuples of self, and matched
        input to path."""
        if not isinstance(word, tuple) or not word[:2]:
            return False
        temp = []
        if not self.head._path_of(word[0:1], temp):
            return False
        elif not self.tail._path_of(word[1], temp):
            return False
        path.extend(temp)
        return self.successor._path_of(word[2:], path)

    def matches(self, ignore):
        """Raises AttributeError."""
        raise AttributeError('ConsPattern must be nested.')


class RestPattern(AbstractCallbacklessPattern, acceptors.AbstractSingle):

    """Only used together with ConsPattern to match nested children.

    Has no successor.

    """
    
    def __init__(self, inner, **kwargs):
        """Instantiated with pattern to match a nested child."""
        self.inner = inner
        super().__init__(**kwargs)

    def _copy_attributes_into(self, copy, dict, **kwargs):
        kwargs['inner'] = self.inner._copy(dict)
        super()._copy_attributes_into(copy, dict, **kwargs)

    def _path_of(self, word, path):
        """True, if matches word.  Appends tuples of self, and matched
        input to path."""
        node = word
        while node:
            temp = []
            if self.inner._path_of((node,), temp):
                path.append((self, node))
                path.extend(temp)
                return True
            else:
                if isinstance(node, tuple):
                    node = node[1]
                else:
                    return False
        return False

    def _repr(self, recur):
        ## Need not add to recur, because other, patterns (Nested,
        ## Lit, Tup,..)  will always be traversed before.
        return '(..{})'.format(self.inner._repr(recur))

    def matches(self, ignore):
        """Raises AssertionError."""
        assert(False) ## Should not be able to access RestPattern.


"""A pattern that matches any object.  Like the regular expression
dot."""
_ = AnyPattern()

"""A pattern that matches input of any length.  Alike the regular
expression .*"""
more = ~_

