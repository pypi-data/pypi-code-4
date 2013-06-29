#!/usr/bin/env python

# Copyright Abel Deuring 2012
# python-ptp-chdk is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2 of the License.

import os
import re
import sys
import unittest


class FilteringTestLoader(unittest.TestLoader):
    def __init__(self, re_pattern):
        super(FilteringTestLoader, self).__init__()
        self._filter_re = re.compile(re_pattern)

    def _flatten(self, test):
        if getattr(test, '__iter__', None) is not None:
            for elem in test:
                if getattr(elem, '__iter__', None) is not None:
                    for e2 in self._flatten(elem):
                        yield e2
                else:
                    yield elem
        else:
            yield test

    def _find_tests(self, start_dir, pattern):
        for test in self._flatten(
                super(FilteringTestLoader, self)._find_tests(start_dir,
                                                             pattern)):
            name = '%s.%s.%s' % (test.__class__.__module__,
                                 test.__class__.__name__,
                                 test._testMethodName)
            if self._filter_re.search(name):
                yield test


main_dir = os.path.split(__file__)[0]
os.chdir(main_dir)

# We expect exactly one directory name starting with 'lib'. Otherwise,
# it's hard to figure out where to expect the libraries.

try:
    lib_dirs = os.listdir('build')
except OSError, value:
    if str(value).find('No such file or directory') >= 0:
        print >>sys.stderr, (
            "Can't find build directory. Run 'setup.py build'.")
        sys.exit(1)
    else:
        raise
lib_dirs = [d for d in lib_dirs if d.startswith('lib')]
if len(lib_dirs) == 0:
    print >>sys.stderr, "Can't find libraries to test. Run 'setup.py build'"
    sys.exit(1)
if len(lib_dirs) > 1:
    print >>sys.stderr, "Found more than directory with built libraries."
    print >>sys.stderr, "Don't know which one to choose."
    sys.exit(1)

sys.path.insert(0, 'py')
sys.path.insert(0, os.path.join('build', lib_dirs[0]))

test_pattern = 'test*.py'
if len(sys.argv) > 1:
    suite = FilteringTestLoader(sys.argv[1]).discover('tests', test_pattern)
else:
    suite = unittest.defaultTestLoader.discover('tests', test_pattern)
unittest.TextTestRunner(verbosity=2).run(suite)
