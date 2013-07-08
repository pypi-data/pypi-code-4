# __init__.py: Make pybc a module.

# Export everything on the "pybc.py" file as being under "pybc" instead of
# "pybc.pybc"
from pybc import *

# Define all our submodules for importing. Currently just a submodule for
# Bitcoin-alikes. Don't make the testing scripts under testing/ importable.
__all__ = ["coin"]
