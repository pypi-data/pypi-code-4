import unittest

import numpy as np
from interpolation.multilinear import mlinspace
from interpolation.splines import MultivariateSplines

from numpy.testing import assert_equal
d = 2

smin = [0]*d
smax = [1]*d
orders = [50]*d

svec = mlinspace( [0]*d, [1]*d, orders)

f = lambda x:  np.atleast_2d( (x**2).sum(axis=0) )
#f = lambda x:  np.atleast_2d( x**2 )
values = f(svec)
splines = MultivariateSplines(smin,smax,orders)
splines.set_values(values)
s0 = np.array([[0],[0]]).copy()
expected = splines(s0)


class Test(unittest.TestCase):

    def test_1(self):

        s0 = [0,0]
        res = splines(s0)

    def test_2(self):

        s0 = np.array([0,0])
        res = splines(s0)

    def test_3(self):

        s0 = np.array([[0,0]])
        res = splines(s0)
        assert_equal(res, expected)

    def test_4(self):

        s0 = np.array([[0,0]]).T
        res = splines(s0)
        assert_equal(res, expected)
