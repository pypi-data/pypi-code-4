#!/usr/bin/env python
import pip
import sys


def main(initial_args=None):
    if 'install' in sys.argv:
        index_set = False
        for piece in sys.argv:
            if '--index-url=' in piece:
                index_set = True

        if not index_set:
            sys.argv.append('--index-url=https://simple.crate.io')
    return pip.main(initial_args)

