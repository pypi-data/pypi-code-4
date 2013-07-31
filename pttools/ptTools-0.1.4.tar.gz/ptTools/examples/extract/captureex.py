#!/usr/bin/env python3

"""A quick demo of finding a pattern in a python source file.

0. First we create a pattern that matches its own declaration in this
   very demo file.  This file contains a pattern which matches itself.
   The pattern is given a callback function that appends the matched
   parse tree branch to a list.

1. We try to match that pattern object against this file's parsetree,
   capturing the matched parse tree node in a list.

2. From the matched parsetree node we can reconstruct and recompile
   the source code to create another pattern object.

3. To assert that the compilation result is equivalent, we match the
   recompiled pattern against this file's parsetree, again.

"""

import symbol
import token
import sys

from ptTools import parsetree
from ptTools.parsetree import NonTerminalNode
from ptTools.writers  import AnsiParseTreeWriter
from ptTools.patterns import AnyPattern as Any
from ptTools.patterns import LiteralPattern as Lit
from ptTools.patterns import TuplePattern
from ptTools.patterns import TuplePattern as Tup

from prettify import patterns as prettify


if __name__ == '__main__':

    print(__doc__)

    ## Initializing writer for printing ParseTreeNodes:
    writer = AnsiParseTreeWriter(sys.stdout)
    ## Creating a ParseTreeNode from this very file:
    root = parsetree.fromfile(__file__, attr_type=dict)
    ## Creating a pattern that matches itself in this file:
    _ = Any() 
    captures = []
    X = _%captures.append
    pattern = Tup(symbol.expr_stmt,
                  Tup(Lit(symbol.testlist_star_expr)
                      >> (token.NAME, 'pattern')),
                  (token.EQUAL, '='),
                  X)
    ## Matches parse tree node described by:
    ##
    ##   (expr.stmt
    ##       (testlist_star_expr
    ##           (.. (NAME, 'pattern')),
    ##       (EQUAL '='),
    ##       .)
    ##
    ## Where .. indicates arbitrary depth of the succeeding pattern,
    ## and . stands for any tuple or literal.


    ## Traversing the parsetree, and trying to match the pattern in
    ## every node.  Every match of X is appended to captures.
    #root.preorder_do(pattern.match)
    root.preorder_do(lambda n : [p.match(n) for p in [pattern] + prettify])
    assert(len(captures) == 1)
    match = captures[0]
    print('\n1. Captured by original pattern:')
    writer.write_node(match) 
    writer.write_newline()


    ## Reconstructing source code from the captured node:
    s = match.tostring()
    print('\n2. Reconstructed source of parsetree node:\n{}'.format(s))    


    ## Recompiling the captured node in this scope to a pattern:
    recompiled_pattern = match.recompile(globals())
    assert(isinstance(recompiled_pattern, TuplePattern))
    assert(recompiled_pattern is not pattern)
    assert(str(recompiled_pattern) == str(pattern))
    ## Matching the recompiled pattern again against this file:
    captures.pop()
    root.preorder_do(pattern.match)
    print('\n3. Captured by recompiled pattern:')
    writer.write_node(captures[0])
    writer.write_newline() 
