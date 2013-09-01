"""General tests for the `fix.util` module."""

from types import ModuleType

import fix.util


def test_exists():
    """`fix.util` module exists"""
    assert isinstance(fix.util, ModuleType)
