from __future__ import absolute_import

from celery.utils.dispatch.saferef import safe_ref
from celery.tests.utils import Case


class Class1(object):

    def x(self):
        pass


def fun(obj):
    pass


class Class2(object):

    def __call__(self, obj):
        pass


class SaferefTests(Case):

    def setUp(self):
        ts = []
        ss = []
        for x in xrange(5000):
            t = Class1()
            ts.append(t)
            s = safe_ref(t.x, self._closure)
            ss.append(s)
        ts.append(fun)
        ss.append(safe_ref(fun, self._closure))
        for x in xrange(30):
            t = Class2()
            ts.append(t)
            s = safe_ref(t, self._closure)
            ss.append(s)
        self.ts = ts
        self.ss = ss
        self.closureCount = 0

    def tearDown(self):
        del self.ts
        del self.ss

    def testIn(self):
        """Test the "in" operator for safe references (cmp)"""
        for t in self.ts[:50]:
            self.assertTrue(safe_ref(t.x) in self.ss)

    def testValid(self):
        """Test that the references are valid (return instance methods)"""
        for s in self.ss:
            self.assertTrue(s())

    def testShortCircuit(self):
        """Test that creation short-circuits to reuse existing references"""
        sd = {}
        for s in self.ss:
            sd[s] = 1
        for t in self.ts:
            if hasattr(t, 'x'):
                self.assertIn(safe_ref(t.x), sd)
            else:
                self.assertIn(safe_ref(t), sd)

    def testRepresentation(self):
        """Test that the reference object's representation works

        XXX Doesn't currently check the results, just that no error
            is raised
        """
        repr(self.ss[-1])

    def _closure(self, ref):
        """Dumb utility mechanism to increment deletion counter"""
        self.closureCount += 1
