""" Contains main functions and facilities you will need when using
:mod:`pyquchk`. They all can be imported with ``from pyquchk import ...``,
no need to specify exact modules.
"""

from .qc_decorator import qc
from .checker import for_all, Checker, Result, CheckError, ReturnedFalse
