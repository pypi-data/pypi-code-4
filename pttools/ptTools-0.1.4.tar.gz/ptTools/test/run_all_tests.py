#!/usr/bin/env python3

"""Tests the entire ptTools package."""

import doctest
import sys
import unittest


## Parsetree tests
## ---------------
## Testing parse tree datamodel, creation, accessing, traversal,
## conversion, and iteration, as well as tuple traversal.
## 
from parsetree import TupleTraversalTest
from parsetree import ParseTreeNodeTest
## The following test takes a while:
## from parsetree import ParseTreeNodeLibraryTest


## Pattern tests
## -------------
## Testing pattern datamodel, instantiation, copying, public protocol:
## matching, and callback functions.
##
from misc.acceptors import RegularLanguageAcceptorTest
from patterns import AnyPatternTest
from patterns import ClosurePatternTest
from patterns import ConcatenationPatternTest
from patterns import LiteralPatternTest
from patterns import TailPatternTest
from patterns import TestPatternTest
from patterns import TuplePatternTest
from patterns import UnionPatternTest


## Tokenizer tests
## ---------------
## Tested implicitly by writer.


## Writer tests
## ------------
## The following tests takes a while:
## from ptTools.examples.test import VerboseParseTreeWriterTest
## from ptTools.examples.test import AnsiParseTreeWriterTest


## Pattern matching tests
## ----------------------
from ptpatterns import PatternMatchTest
## The following test takes a while:
## from ptpatterns import ParseTreeNodeLibraryTest


## DocTests
## --------
import ptTools.doc as ptTools_doctest
import ptTools.parsetree as parsetree_doctest
from ptTools.misc import acceptors as acceptor_doctest
from ptTools.patterns import patterns as pattern_doctest
from ptTools.doc.examples import classdef
from ptTools.doc.examples import for_stmt
from ptTools.doc import operators
from ptTools.doc import implementation
from ptTools.doc import todo

def load_tests(loader, tests, ignore):
    modules = [
        acceptor_doctest,
        parsetree_doctest,
        pattern_doctest,
        ptTools_doctest,
        for_stmt,
        classdef,
        operators,
        implementation,
        todo,
        ]
    for mod in modules:
        tests.addTests(doctest.DocTestSuite(mod))
        pass
    return tests

if __name__ == '__main__':
    
    unittest.main()
