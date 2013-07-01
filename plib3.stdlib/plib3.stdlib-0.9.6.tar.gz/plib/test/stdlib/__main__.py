#!/usr/bin/env python3
"""
Module MAIN
Sub-Package TEST.STDLIB of Package PLIB3
Copyright (C) 2008-2013 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This is the test-running script for the PLIB3.STDLIB test suite.
"""


if __name__ == '__main__':
    from plib.test.support import run_tests
    
    modules_with_doctests = [
        'plib.stdlib.classtools',
        'plib.stdlib.coll._tuples',
        'plib.stdlib.decotools',
        'plib.stdlib.iters',
        'plib.stdlib.localize'
    ]
    
    run_tests(__name__, modules_with_doctests)
