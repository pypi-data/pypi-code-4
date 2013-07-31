footer = """\

.. _`more examples`:

More examples
=============

 Also, see ``ptTools.examples``:

 * ``ptTools.examples.pycat`` is a colorizer printing python source
   code to the command line.  Performance is worse than that of e.g.
   `pygmentize <http://pygments.org/>`_.  However, it may be a good starting point when
   designing patterns and visualizing their matches in a source file.
  
 * ``ptTools.examples.extract`` demonstrates recompilation of a
   captured segment.

 Both examples are executable.

"""

def _mkreadme(out):
    out.write('.. _examples:\n')
    from . import for_stmt
    for_stmt._mkreadme(out)
    from . import classdef
    classdef._mkreadme(out)
    out.write(footer)
