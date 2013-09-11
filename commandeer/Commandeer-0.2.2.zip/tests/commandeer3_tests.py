"""
Tests specific to commandeer under Python3
"""

import unittest
import commandeer


class TestFuncSpec3(unittest.TestCase):
    
    def test_one_arg_vararg_one_kwarg(self):
        def f(a1, *args, a2=None):
            pass
        accepts_args, args, defaults, kwargs, all_args = commandeer._funcspec(f)
        self.assertTrue(accepts_args)
        self.assertEqual(args, ['a1'])
        self.assertDictEqual(defaults, dict())
        self.assertDictEqual(kwargs, {'a2': None})
        self.assertEqual(all_args, ['a1', 'a2'])

    def test_one_arg_vararg_one_kwarg_kwargs(self):
        def f(a1, *args, a2=None, **kwargs):
            pass
        accepts_args, args, defaults, kwargs, all_args = commandeer._funcspec(f)
        self.assertTrue(accepts_args)
        self.assertEqual(args, ['a1'])
        self.assertDictEqual(defaults, dict())
        self.assertDictEqual(kwargs, {'a2': None}, "f does not accept kwargs")
        self.assertEqual(all_args, ['a1', 'a2'])

    def test_one_arg_defaults_vararg_one_kwarg_kwargs(self):
        def f(a1, a2=None, *args, a3=None, **kwargs):
            pass
        accepts_args, args, defaults, kwargs, all_args = commandeer._funcspec(f)
        self.assertTrue(accepts_args)
        self.assertEqual(args, ['a1'])
        self.assertDictEqual(defaults, {'a2': None})
        self.assertDictEqual(kwargs, {'a3': None})
        self.assertEqual(all_args, ['a1', 'a2', 'a3'])

    def test_one_arg_defaults_one_kwarg_vararg_kwargs(self):
        def f(a1, a2=None, a3=None, *args, **kwargs):
            pass
        accepts_args, args, defaults, kwargs, all_args = commandeer._funcspec(f)
        self.assertTrue(accepts_args)
        self.assertEqual(args, ['a1'])
        self.assertDictEqual(defaults, {'a2': None, 'a3': None})
        self.assertDictEqual(kwargs, dict(), "f does not accept kwargs")
        self.assertEqual(all_args, ['a1', 'a2', 'a3'])
    