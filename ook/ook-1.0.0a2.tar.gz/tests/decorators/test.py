"""General tests for the `ook.decorators` module."""

from types import ModuleType

import ook.decorators


def test_exists():
    """`ook.decorators` module exists"""
    assert isinstance(ook.decorators, ModuleType)
