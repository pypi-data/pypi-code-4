#!/usr/bin/env python3

import parser
import sys
import unittest

from io import StringIO

import ptTools
from ptTools.writers import AnsiParseTreeWriter
from ptTools.writers import VerboseParseTreeWriter
from ptTools.test.testlib import python_library
from ptTools.tokenizer import generate_tokens

from ptTools.examples import pycat


EXCLUDE = (
    'smtpd.py', # File contains strange special characters.
    )

    
class AbstractWriterTest(unittest.TestCase):

    """Provides private helper methods."""

    def _cat(self, path, patterns=[]):
        """Returns cat() output without assertions."""
        with StringIO() as out:
            writer = self._make_writer(out)
            pycat.cat(path, generate_tokens, patterns, writer)
            actual = out.getvalue()
            return actual

    def _make_writer(self, out, styles):
        """Subclass responsibility."""
        raise AttributeError
    
    def assert_identical_parse_trees(self, path, patterns=[]):
        """Asserts equality of recompiled writer output to the
        original parse tree."""
        with open(path, 'r') as f:
            expected = parser.suite(f.read())
            try:
                actual = parser.suite(self._cat(path, patterns))
            except SyntaxError:
                self.fail('recompilation of {} failed'.format(path))
            #self.assertEqual(actual, expected)
            self.assertTrue(actual == expected) # To avoid unreadable output.
        
    def assert_identical_cat(self, path, patterns=[]):
        """Asserts equality of writer output str to the original file
        contents."""
        with open(path, 'r') as f:
            expected = f.read()            
            actual = self._cat(path, patterns)
            #self.assertEqual(actual, expected)
            self.assertTrue(actual == expected) # To avoid unreadable output.


class VerboseParseTreeWriterTest(AbstractWriterTest):

    def _make_writer(self, out):
        return VerboseParseTreeWriter(out)

    def test_library(self):
        """Tests recompilation and verbosity of output for all .py
        files in library root."""
        for py in python_library(EXCLUDE):
            sys.stdout.write('{}...'.format(py))            
            self.assert_identical_parse_trees(py)
            self.assert_identical_cat(py)
            print('PASS')            


class AnsiParseTreeWriterTest(AbstractWriterTest):

    def _make_writer(self, out):
        return AnsiParseTreeWriter(out)
        
    def test_library(self):
        """Tests recompilation of output for all .py files in library
        root."""
        for py in python_library(EXCLUDE):
            sys.stdout.write('{}...'.format(py))
            self.assert_identical_cat(py, [])
            self.assert_identical_parse_trees(py, [])
            print('PASS')            


if __name__ == '__main__':

    ## TODO - Allow arguments to test specific file.

    unittest.main()
