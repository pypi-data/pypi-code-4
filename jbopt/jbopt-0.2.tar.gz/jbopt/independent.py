"""
Custom minimization algorithms in jbopt

minimization routines that assume the parameters to be mostly independent from 
each other, optimizing each parameter in turn.
"""

import numpy

def opt_normalizations(params, func, limits, abandon_threshold=100, noimprovement_threshold=1e-3,
	disp=0):
	"""
	**optimization algorithm for scale variables (positive value of unknown magnitude)**
	
	Each parameter is a normalization of a feature, and its value is sought.
	The parameters are handled in order (assumed to be independent), 
	but a second round can be run.
	Various magnitudes of the normalization are tried. If the normalization converges
	to zero, the largest value yielding a comparable value is used.

	Optimizes each normalization parameter in rough steps 
	using multiples of 3 of start point
	to find reasonable starting values for another algorithm.
	
	parameters, minimization function, parameter space definition [(lo, hi) for i in params]
	
	:param abandon_threshold:
		if in one direction the function increases by this much over the best value, 
		abort search in this direction
	:param noimprovement_threshold:
		when decreasing the normalization, if the function increases by less than 
		this amount, abort search in this direction
	:param disp:
		verbosity
	"""
	newparams = numpy.copy(params)
	lower = [lo for lo, hi in limits]
	upper = [hi for lo, hi in limits]
	for i, p in enumerate(params):
		startval = p
		beststat = func(newparams)
		bestval = startval
		if disp > 0: print '\t\tstart val = %e: %e' % (startval, beststat)
		go_up = True
		go_down = True
		# go up and down in multiples of 3
		# once that is done, refine in multiples of 1.1
		for n in list(3.**numpy.arange(1, 20)) + [None] + list(1.1**numpy.arange(1, 13)):
			if n is None:
				startval = bestval
				if disp > 0: print '\t\trefining from %e' % (startval)
				go_up = True
				go_down = True
				continue
			if go_up and startval * n > upper[i]:
				if disp > 0: print '\t\thit upper border (%e * %e > %e)' % (startval, n, upper[i])
				go_up = False
			if go_down and startval / n < lower[i]:
				if disp > 0: print '\t\thit lower border (%e / %e > %e)' % (startval, n, lower[i])
				go_down = False
			if go_up:
				if disp > 1: print '\t\ttrying %e ^' % (startval * n)
				newparams[i] = startval * n
				newstat = func(newparams)
				if disp > 1: print '\t\tval = %e: %e' % (newparams[i], newstat)
				if newstat <= beststat:
					bestval = newparams[i]
					beststat = newstat
					if disp > 0: print '\t\t\timprovement: %e' % newparams[i]
				if newstat > beststat + abandon_threshold:
					go_up = False
			if go_down:
				if disp > 1: print '\t\ttrying %e v' % (startval / n)
				newparams[i] = startval / n
				newstat = func(newparams)
				if disp > 1: print '\t\tval = %e: %e' % (newparams[i], newstat)
				if newstat + noimprovement_threshold < beststat: # avoid zeros in normalizations
					bestval = newparams[i]
					beststat = newstat
					if disp > 0: print '\t\t\timprovement: %e' % newparams[i]
				if newstat > beststat + abandon_threshold:
					go_down = False
		newparams[i] = bestval
		print '\tnew normalization of %d: %e' % (i, newparams[i])
	print 'optimization done, reached %.3f' % (beststat)
	return newparams

from optimize1d import *

def opt_grid(params, func, limits, ftol=0.01, disp=0, compute_errors=True):
	"""
	see :func:`optimize1d.optimize`, considers each parameter in order
	
	:param ftol: 
		difference in values at which the function can be considered flat
	:param compute_errors:
	 	compute standard deviation of gaussian around optimum
	"""
	caches = [[] for p in params]
	newparams = numpy.copy(params)
	errors = [[] for p in params]
	for i, p in enumerate(params):
		cache = []
		def func1(x0):
			newparams[i] = x0
			v = func(newparams)
			cache.append([x0, v])
			return v
		lo, hi = limits[i]
		bestval = optimize(func1, x0=p,
			cons=[lambda x: x - lo, lambda x: hi - x], 
			ftol=ftol, disp=disp)
		
		if compute_errors:
			errors[i] = cache2errors(func1, cache, disp=disp)
		
		newparams[i] = bestval
		caches[i] = cache
		if compute_errors:
			print '\tnew value of %d: %e [%e .. %e]' % (i, bestval, errors[i][0], errors[i][1])
		else:
			print '\tnew value of %d: %e' % (i, bestval)
	beststat = func(newparams)
	print 'optimization done, reached %.3f' % (beststat)
	
	if compute_errors:
		return newparams, errors
	else:
		return newparams

def opt_grid_parallel(params, func, limits, ftol=0.01, disp=0, compute_errors=True):
	"""
	parallelized version of :func:`opt_grid`
	"""

	import multiprocessing

	def spawn(f):
	    def fun(q_in,q_out):
		while True:
		    i,x = q_in.get()
		    if i == None:
		        break
		    q_out.put((i,f(x)))
	    return fun

	def parmap(f, X, nprocs = multiprocessing.cpu_count()):
	    q_in   = multiprocessing.Queue(1)
	    q_out  = multiprocessing.Queue()

	    proc = [multiprocessing.Process(target=spawn(f),args=(q_in,q_out)) for _ in range(nprocs)]
	    for p in proc:
		p.daemon = True
		p.start()

	    sent = [q_in.put((i,x)) for i,x in enumerate(X)]
	    [q_in.put((None,None)) for _ in range(nprocs)]
	    res = [q_out.get() for _ in range(len(sent))]

	    [p.join() for p in proc]

	    return [x for i,x in sorted(res)]
	
	nthreads = multiprocessing.cpu_count()
	
	caches = [[] for p in params]
	newparams = numpy.copy(params)
	errors = [[] for p in params]
	indices = range(0, len(params), nthreads)
	k = 0
	while k < len(params):
		j = min(len(params), k + nthreads)
		def run1d((i, curparams, curlimits)):
			cache = []
			def func1(x0):
				curparams[i] = x0
				v = func(curparams)
				cache.append([x0, v])
				return v
			lo, hi = curlimits
			bestval = optimize(func1, x0=p,
				cons=[lambda x: x - lo, lambda x: hi - x], 
				ftol=ftol, disp=disp)
		
			if compute_errors:
				errors = cache2errors(func1, cache, disp=disp)
				return bestval, errors, cache
			return bestval, cache
		results = parmap(run1d, [(i, numpy.copy(newparams), limits[i]) for i in range(k, j)])
		for i, r in enumerate(results):
			if compute_errors:
				v, e, c = r
				print '\tnew value of %d: %e [%e .. %e]' % (i, v, e[0], e[1])
			else:
				v, c = r
				e = []
				print '\tnew value of %d: %e' % (i, v)
			newparams[i + k] = v
			caches[i + k] = c
			errors[i + k] = e
		
		k = j
	beststat = func(newparams)
	print 'optimization done, reached %.3f' % (beststat)
	
	if compute_errors:
		return newparams, errors
	else:
		return newparams




