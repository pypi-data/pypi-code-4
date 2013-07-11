#!/usr/bin/env python

from memoise import Cache

@Cache()
def add(a, b, x=1, opt=0):
    return a + b + x + opt

@Cache(timeout=10)
def subst(a, b):
    return a - b

class Test(object):
    @Cache(ignore=[0, "b"])
    def something(self, x, y, a=1, b=2):
        return x + y

print add(12, 4, x=1, opt=1)
print add(12, 4, opt=1, x=1)
print add(12, 4)
print subst(12, 4)
print subst(12, 4)
print Test().something(2, 4, a=0, b=1)
print Test().something(2, 4, b=1, a=0)
