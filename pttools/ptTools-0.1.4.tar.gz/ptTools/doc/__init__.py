#!/usr/bin/env python3
# The following comment is used to auto-create the README.txt file.
"""\

.. _start:

=====================
README for ptTools.py
=====================

.. _intro:

{ptTools}


.. _contents:

**Contents**

    * Two simple examples_
    * Description of the available operators_ (**TODO**)
    * References_
    * License_

..  * A few implementation_ notes (**TODO**)
..  * A todo_ list (**TODO**)


.. _location:

ptTools was written by Markus Rother (python@markusrother.de) and is
located at http://github.com/941design/pttools.  Feedback and
suggestions are welcome.  ptTools requires python3.2.

The object-oriented design of the RegularLanguageAcceptor classes in
``ptTools.misc.acceptors`` was inspired by Lukas Renggli's `Petit
Parser <http://www.lukas-renggli.ch/blog/petitparser-1>`_ written in
Smalltalk.

"""

op_todo = """\

.. _operators:

Available operators
===================

 **TODO**
 
 Please refer to the examples_.  (Also, see
 ``ptTools.misc.acceptors``).

"""

def _mkreadme(out):
    import ptTools
    out.write(__doc__.format(ptTools=ptTools.__doc__))
    from . import examples
    examples._mkreadme(out)
    ## from . import operators
    ## operators._mkreadme(out)
    out.write(op_todo)
    ## from . import implementation
    ## implementation._mkreadme(out)
    from . import references
    references._mkreadme(out)
    ## from . import todo
    ## todo._mkreadme(out)
    from . import license
    license._mkreadme(out)

