from __future__ import absolute_import

try:
    from cPickle import loads, dumps
except ImportError:
    from pickle import loads, dumps

from pystat.tests.base import TestCase
from pystat.counter import Counter


class TestCounter(TestCase):

    def setUp(self):
        super(TestCounter, self).setUp()
        self.counter = Counter()

    def test_add(self):
        self.counter.add()
        self.assertEqual(1, int(self.counter))
        self.counter.add()
        self.assertEqual(2, int(self.counter))

    def test_add_sample(self):
        self.counter.add(5)
        self.assertEqual(5, int(self.counter))

    def test_iadd(self):
        self.counter += 1
        self.assertEqual(1, int(self.counter))

    def test_count(self):
        self.counter.add()
        self.counter.add()
        self.assertEqual(2, len(self.counter))

    def test_serialization(self):
        self.counter.add(1)
        self.counter.add(5)
        self.assertEqual(2, len(self.counter))
        self.assertEqual(1, self.counter.min)
        self.assertEqual(5, self.counter.max)
        dump = dumps(self.counter)
        counter = loads(dump)
        self.assertEqual(2, len(counter))
        self.assertEqual(1, counter.min)
        self.assertEqual(5, counter.max)

    def test_union(self):
        c1 = Counter()
        c2 = Counter()
        c1.add(2)
        c1.add(5)
        c2.add(1)
        c2.add(6)
        c3 = c1.union(c2)
        self.assertEqual(4, len(c3))
        self.assertEqual(14, int(c3))
        self.assertEqual(1, c3.min)
        self.assertEqual(6, c3.max)
