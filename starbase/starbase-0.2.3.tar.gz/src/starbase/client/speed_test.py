import unittest

from six import print_

import simple_timer

from starbase import Connection

PRINT_INFO = True
TRACK_TIME = True

def print_info(func):
    """
    Prints some useful info.
    """
    if not PRINT_INFO:
        return func

    def inner(self, *args, **kwargs):
        if TRACK_TIME:
            timer = simple_timer.Timer() # Start timer

        result = func(self, *args, **kwargs)

        if TRACK_TIME:
            timer.stop() # Stop timer

        print_('\n{0}'.format(func.__name__))
        print_('============================')
        if func.__doc__:
            print_('""" {0} """'.format(func.__doc__.strip()))
        print_('----------------------------')
        if result is not None:
            print_(result)
        if TRACK_TIME:
            print_('done in {0} seconds'.format(timer.duration))

        return result
    return inner

class StarbaseClientSpeedTest(unittest.TestCase):
    def setUp(self):
        pass

    @print_info
    def test_batch_insert(self):
        c = Connection()
        t = c.table('speed_test')
        if t.exists():
            t.drop()

        t.create('users', 'groups', 'messages')

        #tm = simple_timer.Timer()

        b = t.batch()

        num_rows = 10000
        for i in range(0, num_rows):
            b.insert(
                'aaa_{0}'.format(i),
                {
                    'users': {'id': '1', 'pass': 'bla'},
                    'groups': {'id': '1', 'role': 'admins'},
                    'messages': {'id': '1', 'from_user': '1', 'subject': 'bla', 'body': 'bla bla bla'},
                }
                )
        r = b.commit(finalize=True)
        #tm.stop()

        #print 'done in {0} seconds'.format(tm.duration)
        #print 'which makes it {0} inserts per second'.format(tm.duration / num_rows)
        #return None

if __name__ == '__main__':
    unittest.main()
