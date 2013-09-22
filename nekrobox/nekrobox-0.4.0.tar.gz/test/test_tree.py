"""
test_tree
------------

Tests for `nekrobox.tree` module.
"""

import os
import shutil
import pytest

from nekrobox import tree


class TestConfigLoader():

    def test_path_walker(self):
        testtree = {"test": {"tree": 10}, "something": 5}
        assert tree.path_walker(testtree, "test tree".split()) == (10, [])
        assert tree.path_walker(testtree, "test tree something".split()) == (10, ["something"])
        assert tree.path_walker(testtree, "something tree".split()) == (5, ["tree"])

        with pytest.raises(KeyError):
            tree.path_walker(testtree, "nothing".split())

        with pytest.raises(KeyError):
            tree.path_walker(testtree, "test nothing".split())

        try:
            raised = False
            tree.path_walker(testtree, "test nothing".split())
        except KeyError as e:
            raised = True
            assert e.args[0] == "nothing"
        assert raised

    def test_tree_add(self):
        expected = {"test": {"tree": {"something": 10}}}
        assert tree.tree_add({}, "test tree".split(), "something", 10) == expected

        testtree = {}
        tree.tree_add(testtree, ["test"], "something", 5)
        assert testtree == {"test": {"something": 5}}
