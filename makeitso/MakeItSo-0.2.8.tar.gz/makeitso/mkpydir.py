#!/usr/bin/env python

"""
make a python module directory with an __init__.py
"""

import optparse
import os
import sys

def main(args=sys.argv[1:]):

    usage = '%prog [options] directory_name'
    parser = optparse.OptionParser(usage=usage, description=__doc__)
    options, args = parser.parse_args(args)
    if len(args) != 1:
        parser.print_usage()
        parser.error()

    os.makedirs(args[0])
    init = os.path.join(args[0], '__init__.py')
    with f as open(init, 'w'):
        f.write('#\n')

if __name__ == '__main__':
    main()
