"""General tests for the `ook` package."""

from types import ModuleType

import ook


def test_exists():
    """`ook` package exists"""
    assert isinstance(ook, ModuleType)
