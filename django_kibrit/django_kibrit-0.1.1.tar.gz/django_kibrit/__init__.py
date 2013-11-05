
"""

Kibrit
======

The module for watching SCM (git, hg, svn).
Use it for control a static's versions.

"""

__version__ = '0.1.1'
__project__ = __name__
__author__ = "Sinan Midillili <sinan@hipo.biz>"
__license__ = "BSD"


def get_backend(name, **kwargs):
    """

    Create and return backend

    """

    from importlib import import_module

    mod = import_module(__name__ + '.' + name)
    import pdb;pdb.set_trace()
    return mod.Backend(**kwargs)