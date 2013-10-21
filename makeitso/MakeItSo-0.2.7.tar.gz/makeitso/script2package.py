#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
make a package from a .py file
"""

### STUB ###
# TODO:
# - thing to make a setup.py from a .py file
# - use makeitso templates -> directory structure

import optparse
import os
import subprocess
import sys

def add_options(parser):
    """add options to the OptionParser instance"""

def main(args=sys.argv[1:]):

    # parse command line options
    usage = '%prog [options] ...'
    class PlainDescriptionFormatter(optparse.IndentedHelpFormatter):
        """description formatter for console script entry point"""
        def format_description(self, description):
            if description:
                return description.strip() + '\n'
            else:
                return ''
    parser = optparse.OptionParser(usage=usage, description=__doc__, formatter=PlainDescriptionFormatter())
    options, args = parser.parse_args(args)

if __name__ == '__main__':
  main()

