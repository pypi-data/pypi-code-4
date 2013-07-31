#!/usr/bin/env python3

"""Misc. helper functions."""

import os
import sys
import parser


def python_library(exclude=[]):
    """Generates .py files on library path."""
    for d in sys.path:
        if os.path.isdir(d):
            for f in os.listdir(d):
                if not f in exclude and f.endswith('.py'):
                    yield d + os.sep + f
        elif os.path.isfile(d):
            if not d in exclude and d.endswith('.py'):
                yield d

def parse(filename):
    """Returns parse tree of file as tuple."""    
    with open(filename, 'r') as f:
        return parse_string(f.read())

def parse_string(s):
    """Returns parse tree of received string as tuple."""
    return parser.suite(s).totuple()


