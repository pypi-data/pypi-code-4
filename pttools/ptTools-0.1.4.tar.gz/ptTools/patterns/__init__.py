#!/usr/bin/env python3

"""Package providing pattern classes for matching against tuples.

tuples must have the form: tup ::= ((tup | LITERAL)*), and can be
arbitrarily nested.

The following classes provide a simple domain specific language to
describe match patterns for tuples of the above form:

    AnyPattern() :: Matches any one object.

    LiteralPattern(arg) :: Matches the literal argument arg, which can
        be any primitive type or an object.  Uses arg.__eq__ for
        comparison.

    TestPattern(fn) :: Matches obj if fn(obj) returns True.

    TuplePattern(*args) :: Matches the tuple (*args), where each arg
        in args may be a literal or another pattern.  Literals, except
        tuples, and lists are replaced with LiteralPatterns.  If arg
        is a tuple, it is replaced by a nested TuplePattern,
        recursively.  If arg is a list, a closure is applied to its
        inner pattern.  See the function createfrom, which is called
        to create patterns from each arg in *args, as well as the
        examples, below.

    UnionPattern(*args) :: Matches one of the patterns described by
        arg in args.  Tuples are replaced by TuplePatterns.  As a
        shorthand the operator | can be used.  The following are
        synonymous: UnionPattern(A, B) and A | B.

Instances of the above classes provide a .matches(arg) method that
returns True, if the pattern matches arg, False otherwise.

Callback functions can be associated with each pattern instance with
the % operator.  The callback function is called if and only if the
overall pattern matches.  Callback order is preorder for nested
patterns.

To create closures over patterns, use __getitem__.  If A is a pattern,
then A[1] matches that pattern exactly twice, A[:1] matches it zero or
one time, and A[1:] matches it one ore more times.  Any positive
integers [a:b] may be used where a <= b.  The closure A[:1] may be
expressed as [A].  Closures may only be applied inside at least one
TuplePattern.

"""

__author__ = "Markus Rother - python@markusrother.de"
__date__ = "06/2013"
__version__ = "0.1"

__all__ = [
    'more',
    '_',
    'AnyPattern',
    'LiteralPattern',
    'PatternSyntaxError',
    'TestPattern',
    'TuplePattern',    
    'UnionPattern',
    ]

from . patterns import more
from . patterns import _
from . patterns import AbstractPattern 
from . patterns import AnyPattern
from . patterns import ConcatenationPattern
from . patterns import LiteralPattern 
from . patterns import TestPattern
from . patterns import TuplePattern
from . patterns import UnionPattern
