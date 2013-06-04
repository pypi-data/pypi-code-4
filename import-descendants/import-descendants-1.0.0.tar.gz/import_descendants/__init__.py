# -*- coding: utf-8 -*-
# (c) 2013 Bright Interactive Limited. All rights reserved.
# http://www.bright-interactive.com | info@bright-interactive.com
import os


__version__ = '1.0.0'


def import_descendants(parent_module, target_globals, target_locals):
    """
    `import *` from all descendant modules of a module.

    src_module: the module whose descendants are to be imported
    target_globals: the target's globals()
     (target means 'place where the imports should be imported to)
    target_locals: the target's locals()
    """
    basedir = os.path.dirname(parent_module.__file__)

    for root_dir, dirs, files in os.walk(basedir):
        relative_dir = root_dir[len(basedir):]
        package = parent_module.__package__ + relative_dir.replace(os.path.sep, '.')
        components = [os.path.splitext(filename) for filename in files]
        modules = [basename for basename, ext in components
                   if ext == '.py' and basename != '__init__']

        # Import the directory module, unless it is src_module itself (this
        # function is commonly used to import the descendants of a module into
        # itself, so if we didn't have this guard then we'd try to import the
        # parent module into itself)
        if root_dir != basedir:
            exec 'from %s import *' % (package,) in target_globals, target_locals

        for module in modules:
            exec 'from %s.%s import *' % (package, module) in target_globals, target_locals
