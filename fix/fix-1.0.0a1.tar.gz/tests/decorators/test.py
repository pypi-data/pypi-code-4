"""General tests for the `fix.decorators` module."""

from types import ModuleType

import fix.decorators


def test_exists():
    """`fix.decorators` module exists"""
    assert isinstance(fix.decorators, ModuleType)
