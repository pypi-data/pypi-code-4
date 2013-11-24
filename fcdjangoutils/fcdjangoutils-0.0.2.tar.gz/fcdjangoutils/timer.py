# -*- coding: utf-8 -*-
import time

class Timer(object):
    def __init__(self, name, active=True):
        self.tm = None
        self.name=name
        self.active=active

    def __enter__(self):
        self.tm = time.time()

    def __exit__(self, a,b,c):
        t2 = time.time()
        if self.active:
            if not a is None:
                print "Timer exited through exception"
            print "Timer", self.name, "took", (t2-self.tm)

