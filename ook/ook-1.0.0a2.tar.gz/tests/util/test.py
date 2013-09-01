"""General tests for the `ook.util` module."""

from types import ModuleType

import ook.util


def test_exists():
    """`ook.util` module exists"""
    assert isinstance(ook.util, ModuleType)
