#!/usr/bin/env python
from mainapp.feeds import *
from mainapp.feeds import utils
import unittest, operator

class mainapp_feeds_TestCase(unittest.TestCase):
    
    def test_get_feed(self):
        feed = get_feed(data=feed_choices)

    def test_with_integers(self):
        feed_1 = get_feed(feed_id=1)
        feed_2 = get_feed(feed_id=2)
        self.failIfEqual(feed_1, feed_2)
    
    def test_get_feed_choices(self):
        data = utils.get_feed_choices()
        self.assertEqual(isinstance(data, list), True)

        feed_choices = utils.get_feed_choices()
        aList = list(map(operator.itemgetter(2,1), feed_choices))
        self.assertNotEqual(aList, feed_choices)

if __name__ == '__main__':
    unittest.main()

