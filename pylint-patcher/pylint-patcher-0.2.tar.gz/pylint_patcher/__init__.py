"""
__init__.py : pylint_patcher top level
"""
from ._version import __version__
from .patcher import Patcher

PATCHFILENAME = ".pylint-ignores.patch"


