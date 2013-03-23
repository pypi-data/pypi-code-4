#!/usr/bin/env python
'Unit test for pydbgr.frame'
import inspect, unittest
from import_relative import import_relative

Mstack = import_relative('lib.stack', '...pydbgr')

class TestStack(unittest.TestCase):

    def test_count_frames(self):
        f = inspect.currentframe()
        frame_count = Mstack.count_frames(f)
        self.assertTrue(Mstack.count_frames(f) > 2)
        self.assertEqual(frame_count-1, Mstack.count_frames(f.f_back))
        self.assertEqual(frame_count-1, Mstack.count_frames(f, 1))
        return

    def test_stack_misc(self):
        f = inspect.currentframe()
        self.assertEqual('startTest', Mstack.get_call_function_name(f))
        self.assertFalse(Mstack.is_exec_stmt(f))
        self.result = False
        exec("self.result = Mstack.is_exec_stmt(inspect.currentframe())")
        self.assertTrue(self.result)
        return

if __name__ == '__main__':
    unittest.main()
