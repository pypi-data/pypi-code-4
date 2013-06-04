#!/usr/bin/env python
"""
TEST.STDLIB.TEST_MODULEPROXY.PY -- test script for ModuleProxy
Copyright (C) 2008-2013 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This script contains unit tests for the ModuleProxy class in
the plib.stdlib sub-package.
"""

import unittest

import ModuleProxy_testmod


class ModuleProxyTest(unittest.TestCase):
    
    def test_proxy(self):
        testdir = dir(ModuleProxy_testmod)
        testnames = ModuleProxy_testmod._names
        testmod = ModuleProxy_testmod._mod
        
        self.assert_('test_var_static' not in testdir)
        self.assert_('test_var_static' not in testnames)
        self.assert_('test_var_static' in dir(testmod))
        self.assertEqual(ModuleProxy_testmod.test_var_static, "Static test variable.")
        self.assertEqual(testdir, dir(ModuleProxy_testmod))
        self.assert_('test_var_static' not in testnames)
        self.assert_('test_var_static' in dir(testmod))
        
        self.assert_('test_var_dynamic' not in testdir)
        self.assert_('test_var_dynamic' in testnames)
        self.assert_('test_var_dynamic' not in dir(testmod))
        self.assertEqual(ModuleProxy_testmod.test_var_dynamic, "Dynamic test variable.")
        self.assert_(testdir != dir(ModuleProxy_testmod))
        self.assert_('test_var_dynamic' in dir(ModuleProxy_testmod))
        self.assert_('test_var_dynamic' not in testnames)
        self.assert_('test_var_dynamic' not in dir(testmod))
        
        testdir = dir(ModuleProxy_testmod)
        
        self.assert_('test_fn' not in testdir)
        self.assert_('test_fn' in testnames)
        self.assert_('test_fn' not in dir(testmod))
        self.assertEqual(ModuleProxy_testmod.test_fn, "Function returning test value.")
        self.assert_(testdir != dir(ModuleProxy_testmod))
        self.assert_('test_fn' in dir(ModuleProxy_testmod))
        self.assert_('test_fn' not in testnames)
        self.assert_('test_fn' not in dir(testmod))
        
        testdir = dir(ModuleProxy_testmod)
        testnames = dict(ModuleProxy_testmod._names)
        testmoddir = dir(ModuleProxy_testmod._mod)
        
        self.assertRaises(AttributeError, getattr, ModuleProxy_testmod, 'this_one_aint_there')
        self.assertEqual(testdir, dir(ModuleProxy_testmod))
        self.assertEqual(testnames, ModuleProxy_testmod._names)
        self.assertEqual(testmoddir, dir(ModuleProxy_testmod._mod))


if __name__ == '__main__':
    unittest.main()
