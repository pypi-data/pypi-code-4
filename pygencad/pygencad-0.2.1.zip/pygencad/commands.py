"""Main PyGenCad entry point.

The commands sub-module provides helper functions for creating CommandFile and
Layer objects targeting specific backends. Functions from the commands
sub-module are available at the top level of the PyGenCAD package.
"""
from . import autocad, microstation, svg

# Mapping of names to backend modules
backends = {
    'autocad':autocad,
    'microstation':microstation,
    'svg':svg,
}
# Mapping of name to preferred backend extension
backext = dict()
for name, backend in backends.items():
    backext[name] = backend.EXT

def get_script(filelike, backend):
    """Return an initialized CommandFile object for the requested backend.

    >>> from pygencad import *
    >>> from StringIO import StringIO
    >>> f = StringIO()
    >>> get_script(f, 'autocad')
    <pygencad.autocad.CommandFile object at 0x...>
    >>> get_script(f, 'spam')
    Traceback (most recent call last):
        ...
    ValueError: Unknown backend ...!

    :param filelike: An object with a write method.
    :type filelike: filelike
    :param backend: Name of the backend to use, must be in pygencad.backends.
    :type backend: string
    :raises: ValueError if the provided name isn't in pygencad.backends
    :returns: An instantiated CommandFile object for the indicated backend.
    """
    if backend.lower() in backends:
        return backends[backend].CommandFile(filelike)
    else:
        raise ValueError("Unknown backend {}!".format(backend))

def get_layer(backend):
    """Return the layer class for the indicated backend.

    >>> from pygencad import *
    >>> from StringIO import StringIO
    >>> f = StringIO()
    >>> get_layer('autocad') # Notice the return isn't an object:
    <class 'pygencad.autocad.Layer'>
    >>> get_script(f, 'spam')
    Traceback (most recent call last):
        ...
    ValueError: Unknown backend ...!

    :param backend: Name of the backend to use, must be in pygencad.backends.
    :type backend: string
    :raises: ValueError if the provided name isn't in pygencad.backends
    :returns: Layer class for the indicated backend.
    """
    # This is for creating persistent layer objects outside a script
    # To make an anonymous layer just use script.set_layer(args) instead
    if backend.lower() in backends:
        return backends[backend].Layer
    else:
        raise ValueError("Unknown backend {}!".format(backend))

