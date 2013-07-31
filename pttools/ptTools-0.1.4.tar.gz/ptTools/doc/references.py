#!/usr/bin/env python3
# The following comment is used to auto-create the README.txt file.
"""\

.. _references:

References
==========

  * For the complete python grammar see:
    http://docs.python.org/3.2/reference/grammar.html

  * Nonterminals can be found in: ``/usr/include/python3.2/graminit.h`` as
    well as in the module: ``symbol``.
  
  * Reference for terminals is found in the modules: ``token`` and
    ``tokenize``.

"""

def _mkreadme(out):
    out.write(__doc__)
