################################################################
# pp.core - Produce & Publish
# (C) 2013, ZOPYX Limited, www.zopyx.com
################################################################

import tempfile
from pp.core.resources_registry import resources_registry
from pp.core.resources_registry import registerResource
import pytest

def test_empty():
    assert len(resources_registry) == 0

def test_insert():
    resources_registry.clear()
    registerResource('foo', tempfile.gettempdir())

def test_insert_twice():
    resources_registry.clear()
    registerResource('foo', tempfile.gettempdir())
    with pytest.raises(KeyError):
        registerResource('foo', tempfile.gettempdir())
