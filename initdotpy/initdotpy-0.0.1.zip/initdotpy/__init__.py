"""The initdotpy package makes it simple to write __init__.py files that automatically include the package contents.

For example if you have an __init__.py that looks like::

import submodule1 
import submodule2 
import submodule3 
import subpackage1
import subpackage2
import subpackage3

You can replace it with::

from initdotpy import auto_import
auto_import()

and it will automatically import all the modules/packages contained in the package and stay up to date when you make changes to the package contents.

Or if you prefer to import the contents of the submodules/subpackages, e.g.::

from submodule1 import *
from submodule2 import *
from submodule3 import *
from subpackage1 import *
from subpackage2 import *
from subpackage3 import *

You can just write your __init__.py as::

from initdotpy import auto_import_contents
auto_import_contents()

Again this __init__.py automatically stays up to date so you need never edit it again."""
import os
import sys
import pkgutil
import inspect
 
 
__all__ = ['auto_import', "auto_import_contents"]


def auto_import(exclude=tuple()):
    """If you have an __init__.py that looks like::
    
    import submodule1 
    import submodule2 
    import submodule3 
    import subpackage1
    import subpackage2
    import subpackage3
    
    You can replace it with::
    
    from initdotpy import auto_import
    auto_import()
    
    and it will automatically import all the modules/packages contained in the package and stay up to date when you make changes to the package contents."""
    
    def add_child_to_parent(parent_module, child, child_module):
        setattr(parent_module, child, child_module)
        parent_module.__all__.append(child)
    
    _auto_import_impl(add_child_to_parent, False, exclude, auto_import)


def auto_import_contents(exclude=tuple()):
    """If you have an __init__.py that looks like::
    
    from submodule1 import *
    from submodule2 import *
    from submodule3 import *
    from subpackage1 import *
    from subpackage2 import *
    from subpackage3 import *
    
    You can just write your __init__.py as::
    
    from initdotpy import auto_import_contents
    auto_import_contents()
    
    and it will automatically import the contents from all the modules/packages contained in the package and stay up to date when you make changes to the package contents."""
    
    def add_child_contents_to_parent(parent_module, child, child_module):
        if not hasattr(child_module, '__all__'):
            raise RuntimeError("Module or package %s does not define __all__" % child)
        
        duplicates = set(child_module.__all__).intersection(parent_module.__all__)
        if duplicates:
            raise RuntimeError("The following names, defined in %s, are already defined elsewhere: %s"
                               % (child, duplicates))
        else:
            for name in child_module.__all__:
                setattr(parent_module, name, getattr(child_module, name))
                parent_module.__all__.append(name)
    
    _auto_import_impl(add_child_contents_to_parent, True, exclude, auto_import_contents)

 
def _auto_import_impl(func, import_contents, exclude, item_for_removal):
    """Implements auto_import and auto_import_contents"""
    
    parent_module = inspect.getmodule(inspect.stack()[2][0]) 

    if not hasattr(parent_module, '__all__'):
        parent_module.__all__ = []
 
    for module_loader, child, _ in pkgutil.iter_modules([os.path.dirname(parent_module.__file__)]):
        if child not in exclude:
            child_module = module_loader.find_module(parent_module.__name__ + '.' + child).load_module(parent_module.__name__ + '.' + child)
            func(parent_module, child, child_module)

    for attr_name in dir(parent_module):
        attr_value = getattr(parent_module, attr_name)
        if attr_value is item_for_removal and attr_name not in parent_module.__all__:
            delattr(parent_module, attr_name)
