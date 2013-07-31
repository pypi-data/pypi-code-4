"""\

.. _start:

===========================================================
README for ptTools.py (http://github.com/941design/pttools)
===========================================================

{ptTools}

Contents
========

**TODO - hyperlinks**

This readme consists of:
    * examples
    * available operators
    * class layout
    * implementation notes
    * todos
    * module/class comments??

"""

def _mkreadme(out):
    import ptTools
    out.write(__doc__.format(ptTools=ptTools.__doc__))
