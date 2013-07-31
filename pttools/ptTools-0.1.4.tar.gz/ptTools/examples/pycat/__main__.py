#!/usr/bin/env python3

"""Writes ansi-colored .py file to stdout.

Styles are described in pycat/styles.  Patterns for regions to be
styled are defined in pycat/patterns.

"""

import sys

import ptTools
from ptTools.writers import AnsiParseTreeWriter
from ptTools.tokenizer import Tokenizer

from ptTools.examples import pycat
from ptTools.examples.pycat.patterns import node_patterns
from ptTools.examples.pycat.patterns import token_patterns 


if __name__ == '__main__':

    FILENAME  = sys.argv[1]
    WRITER    = AnsiParseTreeWriter(sys.stdout)
    TOKENIZER = Tokenizer(token_patterns, attr_type=dict)
    
    pycat.cat(FILENAME, TOKENIZER, node_patterns, WRITER)

