
import pytest

def test_load( te, std_te_input, std_te_tasks ):
    assert te.load(std_te_input) == std_te_tasks


