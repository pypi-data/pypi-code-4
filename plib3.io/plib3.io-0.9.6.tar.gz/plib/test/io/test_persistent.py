#!/usr/bin/env python3
"""
TEST.IO.TEST_PERSISTENT.PY -- test script for sub-package IO of package PLIB3
Copyright (C) 2008-2013 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This script contains unit tests for the persistent async I/O
classes in the PLIB3.IO sub-package.
"""

import unittest
import select

from plib.io import async

from .testlib import PersistentTest
from .testlib_persistent import ReadWriteTestMixin, TerminatorTestMixin

# Only run these tests if poll is available

if hasattr(select, 'poll'):
    
    async.use_poll(True)  # ensure we use poll (not strictly necessary
                          # since True is the default, just shows usage)
    
    
    class XPersistentTest(ReadWriteTestMixin, PersistentTest, unittest.TestCase):
        
        client_list = [b"Python rocks!", b"Try it today!", b"You'll be glad you did!"]
        server_list = [b"You betcha!", b"It's *much* better than Perl!", b"And don't even *mention* C++!"]
    
    
    class XPersistentTestWithPush(XPersistentTest):
        
        test_auto_push = True
    
    
    class XPersistentTestLargeMessage1(XPersistentTest):
        
        client_list = [b"a" * 6000, b"b" * 6000, b"c" * 6000]
        server_list = [b"1" * 6000, b"2" * 6000, b"3" * 6000]
    
    
    class XPersistentTestLargeMessage2(XPersistentTest):
        
        client_list = [b"a" * 10000, b"b" * 10000, b"c" * 10000]
        server_list = [b"1" * 10000, b"2" * 10000, b"3" * 10000]
    
    
    class YPersistentTest(TerminatorTestMixin, PersistentTest, unittest.TestCase):
        
        client_list = [b"Python rocks!", b"Try it today!", b"You'll be glad you did!"]
        server_list = [b"You betcha!", b"It's *much* better than Perl!", b"And don't even *mention* C++!"]
    
    
    class YPersistentTestWithPush(YPersistentTest):
        
        test_auto_push = True
    
    
    class YPersistentTestLargeMessage1(YPersistentTest):
        
        client_list = [b"a" * 6000, b"b" * 6000, b"c" * 6000]
        server_list = [b"1" * 6000, b"2" * 6000, b"3" * 6000]
    
    
    class YPersistentTestLargeMessage2(YPersistentTest):
        
        client_list = [b"a" * 10000, b"b" * 10000, b"c" * 10000]
        server_list = [b"1" * 10000, b"2" * 10000, b"3" * 10000]


if __name__ == '__main__':
    if not hasattr(select, 'poll'):
        print("Poll not available, skipping persistent I/O tests for poll.")
    unittest.main()
