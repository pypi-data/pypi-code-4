#!/usr/bin/env python3

"""Example use case for pattern matching: colored source code output."""


__author__  = "Markus Rother - python@markusrother.de"
__date__    = "06/2013"
__version__ = "0.1"

__all__=[
    'cat',
    ]

import sys

import ptTools
from ptTools import parsetree


def cat(filename, tokenizer, patterns, writer):
    """Parses file, then applies patterns on parsetree root before
    passing it to writer."""

    ## Parsing:
    root = parsetree.fromfile(filename, tokenizer, attr_type=dict)

    ## Applying patterns:
    if patterns:
        for node in root.preorder():
            for pattern in patterns:
                pattern.match(node)

    ## Writing:
    writer.write_node(root)

