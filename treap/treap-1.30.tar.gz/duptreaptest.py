#!/usr/bin/env python


import sys
import random
import functools
import traceback
import exceptions

import myut
import py_duptreap as duptreap

# must be at least 10 (1e1), or some tests will fail
#n = int(1e1)
n = int(1e1)

def sign(x):
    if x < 0:
        return -1
    elif x > 0:
        return 1
    else:
        return 0

class values_test():
    def create(self, sequence):
        self.treap = duptreap.duptreap()

        for i in sequence:
            self.treap[i] = i

        self.content = list(self.treap)

    def check_first(self, key):
        myut.assertEqual(self.content[0], key)

class stepped_test(values_test):
    def __init__(self, first, last, by):
        self.first = first
        self.last = last
        self.by = by

    def check_steps(self, by):
        for i in xrange(len(self.content)-1):
            # FIXME:
            # this can be simplified a bit, but I just wanted to get something working first ^_^
            if self.by > 0:
                myut.assertEqual(self.content[i], self.content[i+1] - self.by)
            else:
                myut.assertEqual(self.content[i], self.content[i+1] + self.by)

    def runTest(self):
        if self.first > self.last and self.by >= 0:
            sys.exit(1)
        if self.first < self.last:
            r = xrange(self.first, self.last, self.by)
        else:
            r = xrange(self.first, self.last-1, self.by)
        self.create(r)
        if self.first < self.last:
            self.lowest = self.first
            self.highest = (self.last - self.first - 1) / self.by * self.by
        else:
            #self.lowest = (self.last - self.first) % self.by + self.last
            self.lowest = (self.first - self.last) % abs(self.by) + self.last
            self.highest = self.first
        #print 'self.first: %d, self.last: %d, self.by: %d, self.lowest: %d, self.highest: %d' % (self.first, self.last, self.by, self.lowest, self.highest)
        self.check_first(self.lowest)
        self.check_steps(self.by)

def randoms(x):
    for i in xrange(x):
        yield int(random.random() * x)

class direction_test(values_test):
    def __init__(self):
        pass

    def runTest(self):
        self.create(randoms(n))
        expected_direction = [0, 1]
        for i in xrange(len(self.content)-1):
            actual_direction = sign(self.content[i+1] - self.content[i])
            myut.assertTrue(actual_direction in expected_direction)

def random_swaps(lst):
    len_lst = len(lst)
    for i in xrange(len_lst):
        j = int(random.random() * len_lst)
        lst[i], lst[j] = lst[j], lst[i]
    return lst
        
class order_test(values_test):
    # FIXME
    # note that this makes 0 effort to check what happens to duplicate values!
    def __init__(self):
        pass

    def runTest(self):
        unordered_values = list(randoms(n))
        ordered_values = list(unordered_values)
        ordered_values.sort()
        self.create(unordered_values)
        result = ordered_values == self.content
        myut.assertEqual(result, True)

def step_tests():
    for first, last, by in [ (0, n, 1), (0, n, 5), (n, 0, -1), (n, 0, -5) ]:
        st = stepped_test(first, last, by)
        myut.require_exceptionless('1st: %d, nth: %d, by: %d' % (first, last, by), st.runTest)

def direction_tests():
    rt = direction_test()
    myut.require_exceptionless('direction test', rt.runTest)

def order_tests():
    ot = order_test()
    myut.require_exceptionless('order test', ot.runTest)

def print_tests():
    # note that we intentionally ignore n here, because the tree print is pretty huge at large values
    print_test(100)
    
def print_test(n):
    t = duptreap.duptreap()
    for i in xrange(n):
        t[i] = i
    dummy = str(t)

def removal_test():
    t = duptreap.duptreap()
    # fill the treap with 0..n
    for i in xrange(n):
        t[i] = i
    # remove all the odd values
    for i in xrange(1,n,2):
        del t[i]
    # check that we have nothing but even values left
    ordered_values = list(t.iterator())
    result = ordered_values == range(0, n, 2)
    myut.assertEqual(result, True)

def reremoval_test():
    t = duptreap.duptreap()
    # fill the treap with 0..n
    for i in xrange(n):
        t[i] = i
    # remove all the odd values
    for i in xrange(1,n,2):
        del t[i]
    # check that we have nothing but even values left
    dummy = list(t.iterator())
    for i in [ 1, 3, 7 ]:
        myut.require_exceptions(functools.partial(t.remove, i), ( exceptions.LookupError, ))

def removal_from_empty_test():
    t = duptreap.duptreap()
    for i in [ 1, 3, 7 ]:
        myut.require_exceptions(functools.partial(t.remove, i), ( exceptions.LookupError, ))

def successful_removal_from_one_test():
    t = duptreap.duptreap()
    t[5] = 5
    del t[5]

def failed_removal_from_one_test():
    t = duptreap.duptreap()
    t[5] = 5
    myut.require_exceptions(functools.partial(t.remove, 10), ( exceptions.LookupError, ))

def positive_find_test():
    t = duptreap.duptreap()
    for i in xrange(0, n, 2):
        t[i] = i
    for i in xrange(0, n, 2):
        myut.assertEqual(t[i], i)

def negative_find_test():
    t = duptreap.duptreap()
    for i in xrange(0, n, 2):
        t[i] = i
    for i in xrange(1, n, 2):
        myut.require_exceptions(functools.partial(t.find, i), ( exceptions.LookupError, ))

def iterator_test():
    lst = range(n)
    random_lst = random_swaps(lst[:])
    t = duptreap.duptreap()
    for x in random_lst:
        t[x] = x
    lst2 = list(t.iterator())
    myut.assertTrue(lst == lst2)

def reverse_iterator_test():
    lst = range(n)
    lst.reverse()
    random_lst = random_swaps(lst[:])
    t = duptreap.duptreap()
    for x in random_lst:
        t[x] = x
    lst2 = list(t.reverse_iterator())
    myut.assertTrue(lst == lst2)

def min_test():
    lst = range(n)
    random_lst = random_swaps(lst[:])
    t = duptreap.duptreap()
    for x in random_lst:
        t[x] = x
    least = t.find_min()
    myut.assertEqual(least, 0)

def empty_min_test():
    t = duptreap.duptreap()
    myut.require_exceptions(t.find_min, (exceptions.LookupError, ))

def max_test():
    lst = range(n)
    random_lst = random_swaps(lst[:])
    t = duptreap.duptreap()
    for x in random_lst:
        t[x] = x
    least = t.find_max()
    myut.assertEqual(least, n-1)

def empty_max_test():
    t = duptreap.duptreap()
    myut.require_exceptions(t.find_max, (exceptions.LookupError, ))

def duplication_behavior_unique():
    #t = duptreap.duptreap(allow_duplicates=False)
    t = duptreap.duptreap()
    t[1] = 1
    t[2] = 2
    t[2] = 2
    t[3] = 3
    myut.assertTrue(list(t) == [1, 2, 2, 3])

#def duplication_behavior_duplicate():
#    # allowing duplicates is default; we specify anyway
#    t = duptreap.duptreap(allow_duplicates=True)
#    t.insert(1)
#    t.insert(2)
#    t.insert(2)
#    t.insert(3)
#    myut.assertTrue(list(t) == [1, 2, 2, 3])

def string_test():
    def random_char():
        return chr(97 + int(random.random() * 32))

    t = duptreap.duptreap()
    dict = {}
    for i in xrange(n):
        strng = '%s%s' % (random_char(), random_char())
        t[strng] = None
        dict[strng] = None
    lst = dict.keys()
    lst.sort()
    myut.assertTrue(list(t) == lst)

def value_test():
    t = duptreap.duptreap()
    for i in xrange(n):
        t[i] = i*3
    for i in xrange(n):
        myut.assertEqual(t[i], i*3)
        
def remove_min_test():
    # O(n^2) test!
    lst = range(n)
    t = duptreap.duptreap()
    for i in lst:
        t[i] = 0
    # taking advantage of the fact that the keys are the same as our lst indices
    for i in lst:
        if i % (n / 5) == 0:
            myut.assertTrue(t.check_heap_invariant())
            myut.assertTrue(t.check_tree_invariant())
        t.remove_min()
        myut.assertTrue(list(t) == lst[i+1:])

def remove_max_test():
    # O(n^2) test!
    lst = range(n)
    t = duptreap.duptreap()
    for i in lst:
        t[i] = 0
    # taking advantage of the fact that the keys are the same as our lst indices
    for i in lst:
        t.remove_max()
        myut.assertTrue(list(t) == lst[:-(i+1)])

def del_insert_del_insert():
    t = duptreap.duptreap()
    for i in xrange(n):
        t[i] = 0
    for i in xrange(n):
        t.remove_min()
    for i in xrange(n):
        t[i] = 0
    for i in xrange(n):
        t.remove_min()

def empty_test():
    t = duptreap.duptreap()
    myut.assertTrue(not (bool(t) == True))

def nonempty_test():
    t = duptreap.duptreap()
    t[1] = 1
    myut.assertTrue(bool(t) == True)

def remove_sequence_test(reverse):
    t = duptreap.duptreap()
    lst = range(n)
    for item in lst:
        t[item] = 0
    if reverse:
        lst.reverse()
        pop = t.remove_max
    else:
        pop = t.remove_min
    for i in xrange(len(lst)):
        value_from_treap = pop()
        myut.assertEqual((lst[i], 0), value_from_treap)
    myut.assertTrue(not bool(t))

def depth_test():
    # O(n^2), so we don't use n - we use something small.
    # We assume very little about the resulting depths - in particular, even though this datastructure should very nearly always be log2(n) deep, we assume that
    # worst case behavior is possible - IE that depth can be as high as n.  We also don't make any effort to show that an empty treap has a depth of 0
    my_n = min(n, 100)
    for i in xrange(my_n):
        t = duptreap.duptreap()
        for j in xrange(i):
            t[j] = j
        myut.assertTrue(0 <= t.depth() <= i)

def empty_0_test():
    t = duptreap.duptreap()
    myut.assertEqual(t.depth(), 0)

def simple_length_test():
    t = duptreap.duptreap()
    for i in xrange(n):
        myut.assertEqual(len(t), i)
        t[i] = i
    myut.assertEqual(len(t), n)

def repeat_length_test():
    t = duptreap.duptreap()
    for i in xrange(n):
        t[i] = i
    for i in xrange(n):
        t[i] = i
    myut.assertEqual(len(t), n*2)

def min_max_length_test():
    t = duptreap.duptreap()
    for i in xrange(n):
        t[i] = 0
    myut.assertEqual(len(t), n)
    t.remove_min()
    myut.assertEqual(len(t), n-1)
    t.remove_max()
    myut.assertEqual(len(t), n-2)
    
def tests():
    for fn in [ \
        iterator_test,
        reverse_iterator_test,
        step_tests,
        direction_tests,
        order_tests,
        print_tests,
        removal_test,
        reremoval_test,
        removal_from_empty_test,
        successful_removal_from_one_test,
        failed_removal_from_one_test,
        positive_find_test,
        negative_find_test,
        min_test,
        max_test,
        empty_min_test,
        empty_max_test,
        duplication_behavior_unique,
        string_test,
        value_test,
        remove_min_test,
        remove_max_test,
        del_insert_del_insert,
        empty_test,
        nonempty_test,
        functools.partial(remove_sequence_test, reverse=False),
        functools.partial(remove_sequence_test, reverse=True),
        depth_test,
        empty_0_test,
        simple_length_test,
        repeat_length_test,
        min_max_length_test,
        ]:
        try:
            fn()
        except:
            print 'failed:', str(fn)
            traceback.print_exc()
            print '/\\' * 35

tests()

# FIXME: Need to test find_all

