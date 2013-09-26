import scipy
import numpy

"""
likelihood is multivariate, independent gaussian
optimize each param in turn
"""


centers = numpy.array([0.1, 15, 3.3, 4.1, 0])
sigmas  = numpy.array([0.01, 0.1, 3, 10, 10])

eval_cache = []

def like(params):
	eval_cache.append(params)
	return (((params - centers) / sigmas)**2).sum()

from jbopt.independent import *

limits = numpy.array([(0, 1000)]*len(centers))
start = numpy.array([0.1]*len(centers))

def test_normalizations():
	print 'TEST normalization step method'
	print opt_normalizations(start, like, limits, disp=0) #, abandon_threshold=1)
	print 'TEST normalization step method: neval:',
	print len(eval_cache)

	while len(eval_cache) > 0:
		eval_cache.pop()

def test_grid():
	print 'TEST grid using BRENT'
	print opt_grid(start, like, limits, ftol=0.01, disp=0)
	print 'TEST grid using BRENT: neval:',
	print len(eval_cache)

def test_grid_parallel():
	print 'TEST grid using BRENT --- parallel'
	print opt_grid_parallel(start, like, limits, ftol=0.01, disp=0)
	print 'TEST grid using BRENT: neval:',
	print len(eval_cache)

if __name__ == '__main__':
	test_grid()
	test_grid_parallel()

