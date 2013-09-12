#!/usr/bin/env python

"Test sqlliterals."

import sqlliterals.pyparser
import sqlliterals.regexp

def show(regions):
    non_literal = 1
    for region in regions:
        print region,
        if non_literal:
            print "(NL)",
        else:
            print "(L)",
        non_literal = not non_literal
    print

l = [
    "a = a",
    "a = 'a'",
    "'a' = a",
    "'a' = 'a'",
    "a = ''''",
    "'''' = a",
    "'''' = ''''",
    "a = '''a'''",
    "'''a''' = a",
    "'''a''' = '''a'''"
    ]

for s in l:
    show(sqlliterals.pyparser.parseString(s))
    show(sqlliterals.regexp.parseString(s))

l2 = [
    ("a = ?", "a = %s"),
    ("a = '?'", "a = '?'"),
    ("'a' = ?", "'a' = %s"),
    ("'a' = '?'", "'a' = '?'"),
    ("a = ''?''", "a = ''%s''"),
    ("'''' = ?", "'''' = %s"),
    ("'''' = ''?''", "'''' = ''%s''"),
    ("a = '''?'''", "a = '''?'''"),
    ("'''a''' = ?", "'''a''' = %s"),
    ("'''a''' = '''?'''", "'''a''' = '''?'''")
    ]

for s, exp in l2:
    s2 = sqlliterals.pyparser.replace("?", "%s", s)
    print s, s2, s2 == exp
    s2 = sqlliterals.regexp.replace("?", "%s", s)
    print s, s2, s2 == exp

# vim: tabstop=4 expandtab shiftwidth=4
