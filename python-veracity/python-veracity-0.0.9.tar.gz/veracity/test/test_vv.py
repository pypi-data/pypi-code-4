#!/usr/bin/env python

"""
Unit tests for the veracity.vv module.
"""

import unittest
import os

from veracity import vv

from veracity.test import TEST, FILES


INDENTED = """
    bbb789
abc
    8734981296969a696a7685as
123
   bd7675d

"""
TAGS = """
               tag1:     1:abc123
                1.0:     2:456
"""
STAMPS = """
failures:       1
tested: 2
"""
FILES = """
        change1:  + @/path/1
        change2:    @/path2
"""
CHANGESETS = """
        revision:  14:0c340fca
        branch:  build_tracking
        who:  testuser
        when:  2013/03/07 01:51:36.713 +0000
        comment:  added possible CLI for build tracking
        parent:  13:bd0cd7bb50a18b7d4d156db3c106f572ff3ffb04

        revision:  18:518a7e0ed1fe30112
        branch:  master
        branch:  test
        who:  testuser
        when:  2013/06/27 13:57:42.942 +0100
        comment:  fixed a test failure in Windows
        parent:  17:c7ee91e77c61a9b7b1ed85ea7356c57b57a05ee0
"""


class TestCommands(unittest.TestCase):  # pylint: disable=R0904
    """Tests for top-level Veracity commands."""  # pylint: disable=C0103

    def test_repos(self):
        """Verify the list of repositories can be retrieved."""
        self.assertLess(0, len(vv.repos()))

    def test_version(self):
        """Verify the version string is returned."""
        self.assertNotEqual("", vv.version())


class TestRun(unittest.TestCase):  # pylint: disable=R0904
    """Tests for the Veracity wrapper function."""  # pylint: disable=C0103

    def test_exception(self):
        """Verify a VeracityException is raised on an invalid call."""
        os.chdir(TEST)
        self.assertRaises(vv.VeracityException, vv.run, 'not_a_function')


class TestParsing(unittest.TestCase):  # pylint: disable=R0904
    """Tests for parsing Veracity output."""  # pylint: disable=C0103

    def test_none(self):
        """Verify output can be parsed."""
        self.assertEqual(['foo',
                          'bar'], list(vv.parse("foo\nbar")))

    def test_error(self):
        """Verify an unknown format cannot be parsed."""
        self.assertRaises(ValueError, list, vv.parse("foo\nbar", 'unknown'))

    def test_indented(self):
        """Verify indented output can be parsed."""
        self.assertEqual(['abc',
                          '123'], list(vv.parse(INDENTED, 'indented')))

    def test_tags(self):
        """Verify tags output can be parsed."""
        self.assertEqual([('tag1', '1', 'abc123'),
                          ('1.0', '2', '456')], list(vv.parse(TAGS, 'tags')))

    def test_stamps(self):
        """Verify stamps output can be parsed."""
        self.assertEqual([('failures', '1'),
                          ('tested', '2')], list(vv.parse(STAMPS, 'stamps')))

    def test_files(self):
        """Verify file output can be parsed."""
        self.assertEqual([('change1', 'path/1'),
                          ('change2', 'path2')], list(vv.parse(FILES, 'files')))

    def test_changesets(self):
        """Verify changeset output can be parsed."""
        changesets = list(vv.parse(CHANGESETS, 'changesets'))
        self.assertEqual(2, len(changesets))
        self.assertEqual(['18:518a7e0ed1fe30112'], changesets[1]['revision'])
        self.assertEqual(['master', 'test'], changesets[1]['branch'])


if __name__ == '__main__':
    unittest.main()
