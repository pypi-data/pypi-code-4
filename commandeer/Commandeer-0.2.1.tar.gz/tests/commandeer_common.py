"""Test data for Commandeer."""

import unittest
import commandeer

def f1():
    """Just a bogus function we can inspect later."""
    pass
def f2():
    pass
def f3():
    pass

class TestCleaning(unittest.TestCase):
    
    def test_nono_switch(self):
        value, name = commandeer._clean_value('', True, 'name')
        self.assertEqual(value, True, "value of empty string must be true if name doesn't start with 'no'")
        self.assertEqual(name, 'name', "name should stay the same if it doesn't start with 'no'")

    def test_no_switch(self):
        value, name = commandeer._clean_value('', True, 'noname')
        self.assertEqual(value, False, "value of empty string must be false if name starts with 'no'")
        self.assertEqual(name, 'name', "name should lose the 'no' at the beginning")

    def test_string(self):
        value, name = commandeer._clean_value('string', 'default', 'name')
        self.assertEqual(value, 'string', "must be a string")
        self.assertEqual(name, 'name', "name of non-boolean argument must stay the same")

    def test_number_int(self):
        value, name = commandeer._clean_value('2.3', 0, 'name')
        self.assertEqual(value, 2.3, "number, even if default is an int")
        self.assertEqual(name, 'name', "name of non-boolean argument must stay the same")

    def test_number_float(self):
        value, name = commandeer._clean_value('2.3', 0.0, 'name')
        self.assertEqual(value, 2.3, "must be number")
        self.assertEqual(name, 'name', "name of non-boolean argument must stay the same")

    def test_boolean_parsing(self):
        value, name = commandeer._clean_value('on', True, 'noname')
        self.assertEqual(value, True, "on must parse to true")
        self.assertEqual(name, 'noname', "name of parsed boolean must stay the same")
        value, name = commandeer._clean_value('yEs', True, 'noname')
        self.assertEqual(value, True, "yEs must parse to true")
        self.assertEqual(name, 'noname', "name of parsed boolean must stay the same")
        value, name = commandeer._clean_value('TrUe', True, 'noname')
        self.assertEqual(value, True, "TrUe must parse to true")
        self.assertEqual(name, 'noname', "name of parsed boolean must stay the same")
        value, name = commandeer._clean_value('1', True, 'noname')
        self.assertEqual(value, True, "1 must parse to true")
        self.assertEqual(name, 'noname', "name of parsed boolean must stay the same")

        value, name = commandeer._clean_value('off', False, 'noname')
        self.assertEqual(value, False, "off must parse to true")
        self.assertEqual(name, 'noname', "name of parsed boolean must stay the same")
        value, name = commandeer._clean_value('NO', False, 'noname')
        self.assertEqual(value, False, "NO must parse to true")
        self.assertEqual(name, 'noname', "name of parsed boolean must stay the same")
        value, name = commandeer._clean_value('FaLsE', False, 'noname')
        self.assertEqual(value, False, "FaLsE must parse to true")
        self.assertEqual(name, 'noname', "name of parsed boolean must stay the same")
        value, name = commandeer._clean_value('0', False, 'noname')
        self.assertEqual(value, False, "0 must parse to true")
        self.assertEqual(name, 'noname', "name of parsed boolean must stay the same")
        value, name = commandeer._clean_value('-1', False, 'noname')
        self.assertEqual(value, False, "-1 must parse to true")
        self.assertEqual(name, 'noname', "name of parsed boolean must stay the same")

        value, name = commandeer._clean_value('asdfa', False, 'noname')
        self.assertEqual(value, None, "asdfa must parse to None")
        self.assertEqual(name, 'noname', "name of parsed boolean must stay the same")
        value, name = commandeer._clean_value('ein', False, 'noname')
        self.assertEqual(value, None, "ein must parse to None")
        self.assertEqual(name, 'noname', "name of parsed boolean must stay the same")
        value, name = commandeer._clean_value('an', False, 'noname')
        self.assertEqual(value, None, "an must parse to None")
        self.assertEqual(name, 'noname', "name of parsed boolean must stay the same")
        value, name = commandeer._clean_value('foo', False, 'noname')
        self.assertEqual(value, None, "foo must parse to None")
        self.assertEqual(name, 'noname', "name of parsed boolean must stay the same")
        value, name = commandeer._clean_value('2', False, 'noname')
        self.assertEqual(value, None, "2 must parse to None")
        self.assertEqual(name, 'noname', "name of parsed boolean must stay the same")

    
class TestFuncSpec(unittest.TestCase):
    
    def test_simple(self):
        def f():
            pass
        accepts_args, args, defaults, kwargs, all_args = commandeer._funcspec(f)
        self.assertFalse(accepts_args, "f does not accept variable number of arguments")
        self.assertEqual(args, list(), "f does not accept any arguments")
        self.assertDictEqual(defaults, dict(), "f does not accept defaults")
        self.assertDictEqual(kwargs, dict(), "f does not accept kwargs")
        self.assertEqual(all_args, list(), "f does not accept anything")
    
    def test_one_arg(self):
        def f(argument):
            pass
        accepts_args, args, defaults, kwargs, all_args = commandeer._funcspec(f)
        self.assertFalse(accepts_args, "f does not accept variable number of arguments")
        self.assertEqual(args, ['argument'], "f accepts one argument")
        self.assertDictEqual(defaults, dict(), "f does not accept defaults")
        self.assertDictEqual(kwargs, dict(), "f does not accept kwargs")
        self.assertEqual(all_args, ['argument'], "f accepts exactly one argument")

    def test_two_arg(self):
        def f(argument, another):
            pass
        accepts_args, args, defaults, kwargs, all_args = commandeer._funcspec(f)
        self.assertFalse(accepts_args, "f does not accept variable number of arguments")
        self.assertEqual(args, ['argument', 'another'], "f accepts two arguments")
        self.assertDictEqual(defaults, dict(), "f does not accept defaults")
        self.assertDictEqual(kwargs, dict(), "f does not accept kwargs")
        self.assertEqual(all_args, ['argument', 'another'], "f accepts exactly one argument")

    def test_one_kwarg(self):
        def f(argument=None):
            pass
        accepts_args, args, defaults, kwargs, all_args = commandeer._funcspec(f)
        self.assertFalse(accepts_args, "f does not accept variable number of arguments")
        self.assertEqual(args, [])
        self.assertDictEqual(defaults, {'argument': None})
        self.assertDictEqual(kwargs, dict(), "f does not accept kwargs")
        self.assertEqual(all_args, ['argument'])

    def test_one_arg_one_kwarg(self):
        def f(a1, a2=None):
            pass
        accepts_args, args, defaults, kwargs, all_args = commandeer._funcspec(f)
        self.assertFalse(accepts_args, "f does not accept variable number of arguments")
        self.assertEqual(args, ['a1'])
        self.assertDictEqual(defaults, {'a2': None})
        self.assertDictEqual(kwargs, dict(), "f does not accept kwargs")
        self.assertEqual(all_args, ['a1', 'a2'])

    def test_one_arg_defaults_one_kwarg_vararg_kwargs(self):
        def f(a1, a2=None, a3=None, *args, **kwargs):
            pass
        accepts_args, args, defaults, kwargs, all_args = commandeer._funcspec(f)
        self.assertTrue(accepts_args)
        self.assertEqual(args, ['a1'])
        self.assertDictEqual(defaults, {'a2': None, 'a3': None})
        self.assertDictEqual(kwargs, dict(), "f does not accept kwargs")
        self.assertEqual(all_args, ['a1', 'a2', 'a3'])
        
    def test_sample1(self):
        def echo_command(input, timestamp=False, indent='indent', *args, **kwordargs):
            pass
        accepts_args, args, defaults, kwargs, all_args = commandeer._funcspec(echo_command)
        self.assertTrue(accepts_args)
        self.assertEqual(args, ['input'])
        self.assertDictEqual(defaults, {'timestamp': False, 'indent': 'indent'})
        self.assertDictEqual(kwargs, dict(), "f does not accept kwargs")
        self.assertEqual(all_args, ['input', 'timestamp', 'indent'])
            
        
class TestCondensing(unittest.TestCase):
    
    
    def test_notouchy(self):
        testinput = {'onecommand': f1, 'twocommand': f2}
        testoutput = commandeer._condense(testinput)
        self.assertTrue('onecommand' in testoutput)
        self.assertTrue('twocommand' in testoutput)
        
    def test_simple(self):
        testinput = {'onecommand': f1}
        testoutput = commandeer._condense(testinput)
        self.assertTrue('o' in testoutput)

    def test_one(self):
        testinput = {'onecommand': f1, 'obecommand': f2}
        testoutput = commandeer._condense(testinput)
        self.assertTrue('on' in testoutput)
        self.assertTrue('ob' in testoutput)
        self.assertTrue('o' not in testoutput)

    def test_two(self):
        testinput = {'onecommand': f1, 'onacommand': f2, 'onicommand': f3}
        testoutput = commandeer._condense(testinput)
        self.assertTrue('one' in testoutput)
        self.assertTrue('ona' in testoutput)
        self.assertTrue('oni' in testoutput)
        self.assertTrue('on' not in testoutput)
        self.assertTrue('ob' not in testoutput)
        self.assertTrue('o' not in testoutput)
        
    
    
    
class TestArgParsing(unittest.TestCase):
    
    def test_empty(self):
        callfile, command, switches, args = commandeer._argparse(['test.py'])
        self.assertEqual(callfile, 'test.py')
        self.assertEqual(command, '')
        self.assertEqual(switches, {})
        self.assertEqual(args, [])
    
    def test_switchesonly1(self):
        testinput = ['sample.py', '--something=very good', '--somethingelse', '-s', 'good', ]
        callfile, command, switches, args = commandeer._argparse(testinput)
        self.assertEqual(callfile, 'sample.py')
        self.assertEqual(command, '')
        self.assertEqual(switches, {'something': 'very good', 'somethingelse': '', 's': 'good'})
        self.assertEqual(args, [])
    
    def test_arg1(self):
        testinput = ['sample.py', 'help', '--something=very good', '--somethingelse', '-s', 'good', 'somefile', 'someotherfile']
        callfile, command, switches, args = commandeer._argparse(testinput)
        self.assertEqual(callfile, 'sample.py')
        self.assertEqual(command, 'help')
        self.assertEqual(switches, {'something': 'very good', 'somethingelse': '', 's': 'good'})
        self.assertEqual(args, ['somefile', 'someotherfile'])

    def test_arg2(self):
        testinput = ['sample.py', 'cmd', 'a0', '--s0=v 0', 'a1', '--s1', '-s2', 'v2', 'a2',]
        callfile, command, switches, args = commandeer._argparse(testinput)
        self.assertEqual(callfile, 'sample.py')
        self.assertEqual(command, 'cmd')
        self.assertEqual(switches, {'s0': 'v 0', 's1': '', 's2': 'v2'})
        self.assertEqual(args, ['a0', 'a1', 'a2'])

    def test_arg2(self):
        testinput = ['sample.py', '--s-1=abc', 'a0', '--s0=v 0', 'a1', '--s1', '-s2', 'v2', 'a2',]
        callfile, command, switches, args = commandeer._argparse(testinput)
        self.assertEqual(callfile, 'sample.py')
        self.assertEqual(command, '')
        self.assertEqual(switches, {'s-1': 'abc', 's0': 'v 0', 's1': '', 's2': 'v2'})
        self.assertEqual(args, ['a0', 'a1', 'a2'])

    def test_arg3(self):
        testinput = ['sample.py', 'echo', 'something good', '--indent', '4', '--timestamp', ]
        callfile, command, switches, args = commandeer._argparse(testinput)
        self.assertEqual(callfile, 'sample.py')
        self.assertEqual(command, 'echo')
        self.assertEqual(switches, {'indent': '4', 'timestamp': '',})
        self.assertEqual(args, ['something good', ])


if __name__ == '__main__':
    unittest.main()