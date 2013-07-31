#!/usr/bin/env python3
## The following comment is used to compose the README.txt file.
"""\
.. _`previous example`:
.. _`for_stmt`:

A first example - Creating a simple pattern
===========================================

 The following first example matches a for loop in a python source file.
 We will first `create the parsetree`_ as a nested tuple, then
 `create the pattern`_, and finally we will `match the pattern`_
 against the parsetree.

 Our starting point is the corresponding grammar rule, taken from
 http://docs.python.org/3.2/reference/grammar.html:
 ::

    for_stmt: 'for' exprlist 'in' testlist ':' suite ['else' ':' suite]

 Lowercase expressions are non-terminals that can be imported from the
 ``symbol`` module.  Strings represent terminals with a string value.
 Bracketed sub-rules are optional.  For the sake of simplicity we
 disregard the else option in our pattern.  Also, we will replace the
 rules ``exprlist``, ``testlist`` and ``suite`` by wildcards.  


.. _`create the parsetree`:

Creating the parse tree
~~~~~~~~~~~~~~~~~~~~~~~

 Here, the parse tree is created from a short source segment.  The
 result is a nested tuple of the form:
 ::

    node ::= (INT (, (node|STR))*)

 >>> import parser
 ...
 >>> source = '''
 ... for k in range(10):
 ...     print(k)
 ... '''
 >>> root = parser.suite(source).totuple()

 Note, that the ``for_stmt`` non-terminal seen in the rule above, is
 not the grammar's start symbol, but will be nested somewhere in the
 tuple.


.. _`create the pattern`:

Creating a pattern
~~~~~~~~~~~~~~~~~~

 Next, we create a pattern that matches any for-statement without the
 else option.  As a universal wildcard pattern, we instantiate an
 ``AnyPattern()`` and assign it to the underscore.  The ``TuplePattern`` is
 - as the name suggests - a pattern that matches tuples.  It may hold
 other patterns or literal values.
 
 >>> from symbol import for_stmt
 >>> from ptTools.ptpatterns import TuplePattern as Tup
 >>> from ptTools.ptpatterns import AnyPattern as Any
 >>> _ = Any()
 ...
 >>> pattern = Tup(for_stmt, 'for', _, 'in', _, ':', _)
 >>> pattern
 (296, (1, 'for'), _, (1, 'in'), _, (11, ':'), _)

 where the integers originate from the ``symbol`` and ``token`` modules.

 >>> import symbol
 >>> import token
 >>> 296==symbol.for_stmt and 1==token.NAME and 11==token.COLON
 True

 Repeated for comparison:  The rule
 ::

    for_stmt: 'for' exprlist 'in' testlist ':' suite

 is matched by:
 ::

    ```TuplePattern(for_stmt, 'for', _, 'in', _, ':', _)```

 represented as:
 ::

    ```(296, (1, 'for'), _, (1, 'in'), _, (11, ':'), _)```

 Note, that string literals in the pattern declaration are replaced by
 ``TuplePattern`` instances matching the appropriate parsetree nodes.
 If a token  exists, whose string value equals the given string, that
 token's identifier is inserted, otherwise the identifier defaults to
 ``token.NAME``.
 In the above example ``':'`` was replaced by
 ``TuplePattern(token.COLON, ':')``, because the colon exists as a token.
 The fact that ``in`` and ``for`` are keywords, does not mean they do
 exist as tokens, too.


.. _`match the pattern`:

Matching the pattern
~~~~~~~~~~~~~~~~~~~~

 As mentioned earlier, the pattern does not match the entire parsetree.

 >>> pattern.matches(root)
 False

 It does however match somewhere in the parsetree.

 >>> pattern.matches_in(root)
 True
 >>> match = pattern.first_match_in(root)
 >>> isinstance(match, tuple)
 True

 We can retrieve the matched node, but formatting was lost during
 parsing:

 >>> from ptTools.parsetree import tupletraversal 
 >>> ' '.join([s for s in tupletraversal.leaves(match)])
 'for k in range ( 10 ) :   print ( k )  '

"""

def _mkreadme(out):
    out.write(__doc__)
