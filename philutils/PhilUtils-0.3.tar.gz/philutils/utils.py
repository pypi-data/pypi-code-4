#!/usr/bin/env python

import threading
import multiprocessing


class ReverseSemaphore(object):
    def __init__(self, initial_counter_value=0, module=threading):
        if initial_counter_value < 0:
            raise ValueError("reverse semaphore initial value must be >= 0")
        self.__cond = module.Condition(module.Lock())
        self.__value = initial_counter_value

    def acquire(self, blocking=True):
        outey = False
        self.__cond.acquire()
        while self.__value > 0:
            if not blocking:
                break
            self.__cond.wait()
        else:
            self.__value = self.__value + 1
            outey = True
        self.__cond.release()
        return outey

    def release(self):
        self.__cond.acquire()
        self.__value = max(0, self.__value - 1)
        self.__cond.notify()
        self.__cond.release()

    __enter__ = acquire

    def __exit__(self, t, v, tb):
        self.release()
