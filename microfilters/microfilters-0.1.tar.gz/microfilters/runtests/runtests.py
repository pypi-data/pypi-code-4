#!/usr/bin/env python

from __future__ import unicode_literals
import os
import sys
import unittest

# fix sys path so we don't need to setup PYTHONPATH
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))


def usage():
    return """
    Usage: python runtests.py [UnitTestClass].[method]

    You can pass the Class name of the `UnitTestClass` you want to test.

    Append a method name if you only want to test a specific method of that class.
    """

def main():
    if len(sys.argv) == 2:
        test_case = '.' + sys.argv[1]
    elif len(sys.argv) == 1:
        test_case = ''
    else:
        print(usage())
        sys.exit(1)
    failures = unittest.main(module='microfilters.tests.tests' + test_case)

    sys.exit(failures)

if __name__ == '__main__':
    main()
