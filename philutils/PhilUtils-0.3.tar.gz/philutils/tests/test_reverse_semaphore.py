#!/usr/bin/env python

# Name: test_reverse_semaphore.py
# Author: Philip Zerull
# Date Created: Thursday September 26, 2013


import unittest
import threading
from time import sleep
from philutils.utils import ReverseSemaphore
from Queue import Queue, Empty


class ReverseSemaphoreTester(threading.Thread):
    def __init__(self, reverse_semaphore, blocking, queue, value):
        threading.Thread.__init__(self)
        self.acquired = threading.Event()
        self.pushed = threading.Event()
        self.released = threading.Event()
        self.reverse_semaphore = reverse_semaphore
        self.blocking = blocking
        self.result_queue = queue
        self.value = value
        self.daemon = True

    def run(self):
        self.reverse_semaphore.acquire(self.blocking)
        self.acquired.set()
        self.result_queue.put(self.value)
        self.pushed.set()
        self.reverse_semaphore.release()
        self.released.set()


def queue2list(somequeue):
    results = []
    while not somequeue.empty():
        try:
            curval = somequeue.get(False, 0.01)
        except Empty:
            break
        else:
            results.append(curval)
    return results


class ReverseSemaphoreTest(unittest.TestCase):
    def setUp(self):
        self.valuequeue = Queue()

    def create_thread(self, reverse_semaphore, blocking, value):
        outey = ReverseSemaphoreTester(
            reverse_semaphore,
            blocking,
            self.valuequeue,
            value
        )
        return outey

    def test_nonblocking_zero_based_semaphore_does_not_block(self):
        semaphore = ReverseSemaphore()
        newthread = self.create_thread(semaphore, False, 1)
        newthread.start()
        newthread.join()
        resultslist = queue2list(self.valuequeue)
        self.assertEqual(resultslist, [1])

    def test_creating_semaphore_with_negative_value_raises_error(self):
        self.assertRaises(
            ValueError,
            ReverseSemaphore,
            initial_counter_value=-1
        )

    def test_nonblocking_zero_based_semaphore_returns_true(self):
        semaphore = ReverseSemaphore()
        value = semaphore.acquire(False)
        self.assertEqual(value, True)

    def test_nonblocking_nonzero_based_smaphore_returns_false(self):
        semaphore = ReverseSemaphore(5)
        value = semaphore.acquire(False)
        self.assertEqual(value, False)

    def test_that_semaphore_blocks_correctly(self):
        semaphore = ReverseSemaphore()
        semaphore.acquire()
        newthread = self.create_thread(semaphore, True, 1)
        newthread.start()
        self.valuequeue.put(2)
        semaphore.release()
        newthread.join()
        resultslist = queue2list(self.valuequeue)
        self.assertEqual(resultslist, [2, 1])

    def test_waiting_for_other_thread_to_release_semaphore(self):
        semaphore = ReverseSemaphore()
        newthread = self.create_thread(semaphore, True, 1)
        newthread.start()
        newthread.acquired.wait(.05)
        semaphore.acquire()
        self.valuequeue.put(2)
        semaphore.release()
        newthread.join()
        resultslist = queue2list(self.valuequeue)
        self.assertEqual(resultslist, [1, 2])

    def test_waiting_for_other_thread_to_release_using_context_manager(self):
        semaphore = ReverseSemaphore()
        newthread = self.create_thread(semaphore, True, 1)
        newthread.start()
        newthread.acquired.wait(.05)
        with semaphore:
            self.valuequeue.put(2)
        newthread.join()
        resultslist = queue2list(self.valuequeue)
        self.assertEqual(resultslist, [1, 2])

    def test_multiple_threads_blocking_calling_thread(self):
        semaphore = ReverseSemaphore()
        thread1 = self.create_thread(semaphore, False, 2)
        thread2 = self.create_thread(semaphore, False, 2)
        thread3 = self.create_thread(semaphore, True, 2)
        thread1.start()
        thread2.start()
        thread3.start()
        thread3.acquired.wait()
        with semaphore:
            self.valuequeue.put(1)
        resultslist = queue2list(self.valuequeue)
        self.assertEqual(resultslist, [2, 2, 2, 1])
