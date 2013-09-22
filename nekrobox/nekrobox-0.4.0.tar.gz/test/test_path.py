"""
test_path
------------

Tests for `nekrobox.path` module.
"""

import os
import shutil
import pytest

from nekrobox import path


class TestPath():

    def test_backpaths(self):
        paths = list(path.backpaths("/home/nekroze/git/eden"))
        expected = ["/home/nekroze/git/eden",
                    "/home/nekroze/git",
                    "/home/nekroze",
                    "/home",
                    "/"]
        assert paths == expected

    def test_backsearch(self):
        paths = path.backsearch("setup.py", os.getcwd(), checkhome=False)
        assert len(paths) == 1
        assert "nekrobox/setup.py" in paths[0]
