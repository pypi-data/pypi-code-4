#!/usr/bin/env python3
# The following comment is used to auto-create the README.txt file.
"""\

.. _implementation:

Implementation
==============

Parsetree creation
~~~~~~~~~~~~~~~~~~

 * ptTools processes the source code's parse tree and its token stream
   in parallel.  This is necessary, because some information
   (comments, indentation) is no longer present in a parse-tree, but
   in the tokens.

"""

def _mkreadme(out):
    out.write(__doc__)
