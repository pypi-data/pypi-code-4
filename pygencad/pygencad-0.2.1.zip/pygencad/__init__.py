"""Pythonic generation of CAD command scripts.

This module provides a somewhat streamlined interface to generate drawing
command scripts for a number of drawing backends. By default backend details are
simplified by a uniform interface, but one can issue raw or lightly processed
commands to handle special cases.
"""
from commands import *

__version__ = "0.2.1"
