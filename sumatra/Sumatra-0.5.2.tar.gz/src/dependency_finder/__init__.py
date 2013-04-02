"""
The dependency_finder sub-package attempts to determine all the dependencies of
a given script, including the version of each dependency.

For each executable that is supported there is a sub-module containing a
:func:`find_dependencies()` function, and a series of heuristics for finding
version information. There is also a sub-module :mod:`core`, which contains
heuristics that are independent of the language, e.g. where the dependencies are
under version control.

"""

from __future__ import with_statement
import os
import sys
import warnings

from sumatra.dependency_finder import core, neuron, python, genesis, matlab
    

def find_dependencies(filename, executable):
    """
    Return a list of dependencies for a given script and programming language.
    
    *filename*:
        the path to the script whose dependencies should be found.
    *executable*:
        an instance of :class:`~sumatra.programs.Executable` or one of its
        subclasses.

    """
    if "matlab" in executable.name.lower():
        return matlab.find_dependencies(filename, executable)
    elif "python" in executable.name.lower():
        return python.find_dependencies(filename, executable)
    elif executable.name == "NEURON":
        return neuron.find_dependencies(filename, executable)
    elif executable.name == "GENESIS":
        return genesis.find_dependencies(filename, executable)
    else:
        warnings.warn("find_dependencies() not yet implemented for %s" % executable.name)
        return []