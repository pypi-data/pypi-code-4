#!/usr/bin/env python
"""
Module MAIN
Sub-Package TEST.GUI of Package PLIB
Copyright (C) 2008-2013 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This is the test-running script for the PLIB.GUI test suite.
"""


if __name__ == '__main__':
    from plib.test.support import run_tests
    
    modules_with_doctests = []
    
    # TODO: set module_relative and verbosity from command line options
    module_relative = False
    verbosity = 0
    
    run_tests(__name__, modules_with_doctests, module_relative, verbosity)
