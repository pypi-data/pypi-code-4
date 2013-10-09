#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
#
# Author:   Alisue (lambdalisue@hashnote.net)
# URL:      http://hashnote.net/
# Date:     2013-10-07
#
# (C) 2013 hashnote.net, Alisue
#
import numpy as np


def simple_moving_matrix(x, n=10):
    """Create simple moving matrix

    Args:
        x: a numpy array
        n: the number of sample used to make average

    Returns:
        a numpy array
    """
    if x.ndim > 1 and len(x[0]) > 1:
        x = np.average(x, axis=1)
    h = n / 2
    o = 0 if h * 2 == n else 1
    xx = []
    for i in range(h, len(x) - h):
        xx.append(x[i-h:i+h+o])
    return np.array(xx)

def simple_moving_average(x, n=10):
    """
    Calculate simple moving average

    Args:
        x: a numpy array
        n: the number of sample used to make average

    Returns:
        a numpy array
    """
    if x.ndim > 1 and len(x[0]) > 1:
        x = np.average(x, axis=1)
    a = np.ones(n) / float(n)
    return np.convolve(x, a, 'valid')


def __plugin__(registry):
    registry.register('filters.smm', simple_moving_matrix)
    registry.register('filters.sma', simple_moving_average)
    registry.register('filters.simple_moving_matrix', simple_moving_matrix)
    registry.register('filters.simple_moving_average', simple_moving_average)
__plugin__.manually = True

