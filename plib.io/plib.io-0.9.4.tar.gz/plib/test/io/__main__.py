#!/usr/bin/env python
"""
Module MAIN
Sub-Package TEST.IO of Package PLIB
Copyright (C) 2008-2013 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This is the test-running script for the PLIB.IO test suite.
"""


if __name__ == '__main__':
    from plib.test.support import run_tests
    
    run_tests(__name__)
