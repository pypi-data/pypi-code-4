#!/usr/bin/env python3
## The following comment is used to compose the README.txt file.
"""

.. _operators:

Available operators
===================

 The common operations on regular languages are implemented on
 ``ptTools.ptpatterns``.  However, because python does not have
 postfix unary operators, the operator usage is a bit unusual.


Concatenation
~~~~~~~~~~~~~

 Concatenations are useful, when applying other operations, such as a
 repetition_ to a pattern.  Assume, we would like to match consecutive
 assignments.

 >>> 


Positive closure
~~~~~~~~~~~~~~~~
 +r


.. _`Kleene closure`:

Kleene closure
~~~~~~~~~~~~~~
 ~r


Option
~~~~~~
 -r
 [ r ]


Union
~~~~~
 r | s | t


.. _repetition:

Repetition
~~~~~~~~~~
 r * n


Nesting
~~~~~~~
 r >> s


Appending callback
~~~~~~~~~~~~~~~~~~
 r % fn


 (Also, see ``ptTools.misc.acceptors``).
 
"""

def _mkreadme(out):
    out.write(__doc__)
