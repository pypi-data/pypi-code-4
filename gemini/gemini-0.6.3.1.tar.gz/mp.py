#!/usr/bin/env python

import sys
from multiprocessing import Pool
from time import time

K = 50
def CostlyFunction((z,)):
    r = 0
    for k in xrange(1, K+2):
        r += z ** (1 / k**1.5)
    return r


if __name__ == "__main__":
    currtime = time()
    N = 1000000
    po = Pool()
    res = po.map_async(CostlyFunction,((i,) for i in xrange(N)))
    w = sum(res.get())
    print w
    print '2: parallel: time elapsed:', time() - currtime

    currtime = time()
    res = map(CostlyFunction,((i,) for i in xrange(N)))    
    print w
    print '2: serial: time elapsed:', time() - currtime