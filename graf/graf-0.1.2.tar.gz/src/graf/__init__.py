#!/usr/bin/env python
# coding=utf-8
import pkg_resources
pkg_resources.declare_namespace(__name__)
version = pkg_resources.require('graf')[0].version

__all__ = ['version', 'use', 'call']

def use(environment=None):
    """
    Use graf commands in the shell

    Args:
        environment: None or a dictionary instance which indicate the variables.
            if this is not specified, globals() of caller will be used.
    """
    from graf.plugins import registry
    if not environment:
        import inspect
        frame = inspect.stack()[1][0]
        environment = frame.f_globals
    environment.update(registry.raw)


def call(filename, environment=None):
    """
    Call graf script file in this shell

    Args:
        filename: a filename of graf script file
        environment: None or a dictionary instance which indicate the variables.
            if this is not specified, globals() of caller will be used.
    """
    import os
    import sys
    from graf.plugins import registry

    if not environment:
        import inspect
        frame = inspect.stack()[1][0]
        environment = frame.f_globals

    # create global variables
    local = environment.copy()
    #local.update(locals())
    local.update(registry.raw)

    # call script file
    local['__file__'] = filename
    local['__name__'] = '__main__'
    local['__package__'] = None

    # Opne file and read content
    with open(filename, 'r') as f: content = f.read()
    # Add directory of filename into PYTHONPATH
    python_path_stored = sys.path
    sys.path = [os.path.dirname(filename)] + sys.path
    # execute
    execfile(filename, local)
    # Remove directory from PYTHONPATH
    sys.path = python_path_stored
