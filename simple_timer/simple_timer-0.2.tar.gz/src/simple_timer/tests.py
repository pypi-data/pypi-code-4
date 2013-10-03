from __future__ import print_function

__title__ = 'simple_timer.tests'
__version__ = '0.2'
__build__ = 0x000002
__author__ = 'Artur Barseghyan'

import unittest

from simple_timer import Timer

PRINT_INFO = True

def print_info(func):
    """
    Prints some useful info.
    """
    if not PRINT_INFO:
        return func

    def inner(self, *args, **kwargs):
        result = func(self, *args, **kwargs)

        print('\n\n%s' % func.__name__)
        print('============================')
        if func.__doc__:
            print('""" %s """' % func.__doc__.strip())
        print('----------------------------')
        if result is not None:
            print(result)
        print('\n++++++++++++++++++++++++++++')

        return result
    return inner

class SimpleTimerTest(unittest.TestCase):
    """
    Tests of ``simple_timer.Timer`` class.
    """
    def setUp(self):
        pass

    @print_info
    def test_01_ongoing_timer_duration(self):
        """
        Test on-going timer duration.
        """
        workflow = []

        timer = Timer()

        r1 = timer.duration
        self.assertTrue(r1 is not None)
        workflow.append(r1)

        r2 = timer.duration
        self.assertTrue(r2 is not None)
        workflow.append(r2)

        self.assertTrue(r1 != r2)

        return workflow

    @print_info
    def test_02_ongoing_timer_timedelta(self):
        """
        Test on-going timer timedelta.
        """
        workflow = []

        timer = Timer()

        r1 = timer.timedelta
        self.assertTrue(r1 is not None)
        workflow.append(r1)

        r2 = timer.timedelta
        self.assertTrue(r2 is not None)
        workflow.append(r2)

        self.assertTrue(r1 != r2)

        return workflow

    @print_info
    def test_03_stoped_timer_duration(self):
        """
        Test stoped timer duration.
        """
        workflow = []

        timer = Timer()
        timer.stop()

        r1 = timer.duration
        self.assertTrue(r1 is not None)
        workflow.append(r1)

        r2 = timer.duration
        self.assertTrue(r2 is not None)
        workflow.append(r2)

        self.assertTrue(r1 == r2)

        return workflow

    @print_info
    def test_04_stoped_timer_timedelta(self):
        """
        Test stoped timer timedelta.
        """
        workflow = []

        timer = Timer()
        timer.stop()

        r1 = timer.timedelta
        self.assertTrue(r1 is not None)
        workflow.append(r1)

        r2 = timer.timedelta
        self.assertTrue(r2 is not None)
        workflow.append(r2)

        self.assertTrue(r1 == r2)

        return workflow

if __name__ == "__main__":
    # Tests
    unittest.main()
