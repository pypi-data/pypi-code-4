#!/usr/bin/env python
import gc

class Garbage(object):
    def __del__(self):
        pass

range(500000) # Allocates memory
xrange(500000)
a = range(500000) # Reuses memory
b = xrange(500000)
c = range(500000) # Allocated memory
del a
del b
del c
gc.collect()

# Create two garbage objects by creating a reference cycle of objects having a
# __del__ method.
d = Garbage()
d.other = Garbage()
d.other.other = d
d_id = id(d)
del d
gc.collect()
# Break cycle
for d in gc.garbage:
    if id(d) == d_id:
        break
else:
    raise Exception('Python did not generate/detect expected garbage')
del d.other
del d
del gc.garbage[:]
gc.collect()
