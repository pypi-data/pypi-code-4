#!/usr/bin/env python3
# The following comment is used to auto-create the README.txt file.
"""\

.. _`another example`:
.. _`classdef`:

Example two - Processing matched nodes
======================================

 This example demonstrates a slightly more complex pattern
 description, that matches any class definition in python source.  The
 example also shows how to capture matched regions, and apply
 functions to subpatterns.


Pattern definition
~~~~~~~~~~~~~~~~~~

 >>> from symbol import classdef
 >>> from token import NAME
 >>> import ptTools
 >>> from ptTools.ptpatterns import TuplePattern as Tup
 >>> from ptTools.ptpatterns import _
 ...
 >>> pattern = Tup(classdef, 'class', (NAME, _), ['(', [ _ ], ')'], ':', _)

 Compare this pattern to the grammar rule definition of ``classdef`` taken from
 http://docs.python.org/3.2/reference/grammar.html:
 :: 

  classdef: 'class' NAME ['(' [arglist] ')'] ':' suite

 Unless we are interested in the class definition's body, we may
 replace the pattern's tail with another wildcard:

 >>> more = ~_ ## Creating a Kleene Closure over Any().
 ...
 >>> pattern = Tup(classdef, 'class', (NAME, _), more)

..  (Under operators, see `Kleene closure`_).


Adding callback functions
~~~~~~~~~~~~~~~~~~~~~~~~~

 To send the matched regions to callback functions, simply append '``%
 callable``' to a pattern.  For instance, if we would like to print
 the class name from the above example, we would simply write:
 ::

    ```pattern = Tup(classdef, 'class', (NAME, _%print), more)```

 Note, that the left hand side of the ``%`` operator must have been
 evaluated to a PatternObject prior to evaluating the entire
 expression.  If we would like to print the entire terminal node, we
 have to be explicit, and type:
 ::

    ```pattern = Tup(classdef, 'class', Tup(NAME, _)%print, more)```

 Now, assume, one would like to count classes in a module.  For that
 purpose we define an ``inc`` function with the side effect of
 incrementing a counter, and which is to be called every time our
 classdef pattern matches.  All we have to do is to add a callback to
 ``inc`` to the pattern with the ``%`` operator.

 >>> count = 0
 >>> def inc(ignore):
 ...     globals()['count'] += 1
 ...
 >>> pattern = Tup(classdef, 'class', (NAME, _%print), more)%inc

 Note, that this does two things: It prints the classname *and then*
 increments the counter.  The order of the two is determined by the
 traversal order through our parsetree (which is preorder, and hence
 lexical order of the source code).  In other words, ``print`` will be
 called before ``inc``, because the class name is encountered before
 the entire class definition ends.

 Callback functions can be chained (e.g. '``%inc%input``'), and are
 executed in the order of appending.
 

Applying patterns
~~~~~~~~~~~~~~~~~

 As seen in the `previous example`_, PatternObjects have a
 ``.match(node)`` method, that tries to match a parsetree node, and if
 successful applies its callback functions to the matched regions.
 Its return value is ``None``.

 We now appply that method to every node in the parsetree, starting at
 its root.  If the pattern matches in a node, all queued callback
 functions will be called with the matched node as their only
 argument.
 
 >>> cls_lst = []
 ...
 >>> pattern = Tup(classdef, 'class', (NAME, _%cls_lst.append), more)%inc
 >>> pattern
 (329, (1, 'class'), (1, _), ~(_))

 >>> root = ptTools.parsetree.fromfile(ptTools.ptpatterns.ptpatterns.__file__)
 >>> root.preorder_do(pattern.match)
 ...
 >>> 'TuplePattern' in cls_lst
 True

 Currently, five classes are defined in ``ptTools.ptpatterns.ptpatterns``.

 >>> count
 5

"""

def _mkreadme(out):
    out.write(__doc__)
