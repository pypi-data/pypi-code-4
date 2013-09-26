"""
1D optimization, which should be robust against local flatness in the target function, 
but also estimate errors on the final parameter.

We know that there is only one minimum, and it is far from the constraints.
"""

import scipy.optimize, scipy.interpolate
import numpy
import matplotlib.pyplot as plt

def pause():
	import sys
	print 'please press enter: >> ',
	sys.stdin.readline()

def plot_values(values, points, lastpoint, ymax=numpy.nan, ftol=0.05):
	#print 'values:', zip(points, values)
	#print 'last value', points[lastpoint], values[lastpoint]
	plt.figure()
	plt.plot(points, values, 'o--', color='blue')
	plt.plot(points[lastpoint], values[lastpoint], 'o', color='red')
	if numpy.isnan(ymax):
		worst = [v for v in values if v < 1e100]
		ymax = max(worst)
	plt.ylim(min(values)-ftol, ymax+ftol)
	plt.savefig('optimize1d.pdf')
	plt.close()

phi = (1 + 5**0.5) / 2
resphi = 2 - phi

"""
Is this a line within the tolerance --> return False
"""	
def has_curvature(a, b, c, va, vb, vc, ftol, disp):
	ftol = 10000 * ftol
	grad = (vc - va) / (c - a)
	vbpred = grad * (b - a) + va
	curvcrit = numpy.abs(vbpred - vb) > ftol
	if disp > 0: print '\tCurvature checking: %f (tol=%f): ' % (vbpred - vb, ftol), curvcrit
	return curvcrit

def escalate_left(function, a, b, va, vb, cons, lstep, ftol, disp, plot):
	assert va < vb, (va, vb)
	while va < vb: # we have to go left
		if disp > 0: print '   <<< fast forwarding to LEFT <<< '
		b, c = a, b
		vb, vc = va, vb
		lstep += 1
		while any([con(b - lstep) < 0 for con in cons]):
			lstep /= 3
		a = b - lstep
		va = function(a)
		if disp > 5:
			if plot:
				plot_values([va, vb, vc], [a, b, c], lastpoint=0, ftol=ftol)
		if disp > 0: print '	left %f [%f]' % (a, va)
		if va > vb or not has_curvature(a, b, c, va, vb, vc, ftol, disp): # finally, we found the border
			if disp > 0: print ' found left border'
			return [a, b, c], [va, vb, vc]
		if lstep < 1e-4 and c - a < 1e-4 and numpy.abs(vb - va) < 1e-4:
			if disp > 0: print ' WARNING: hit the lower limit of the parameter', lstep, a, b, va, vb
			return [a, b, c], [va, vb, vc]
	return [a, b, c], [va, vb, vc]
def escalate_right(function, b, c, vb, vc, cons, rstep, ftol, disp, plot):
	assert vc < vb, (vc, vb)
	while vc < vb: # we have to go right
		if disp > 0: print '   >>> fast forwarding to RIGHT >>> '
		a, b = b, c
		va, vb = vb, vc
		rstep += 1
		while any([con(b + rstep) < 0 for con in cons]):
			rstep /= 3
		c = b + rstep
		vc = function(c)
		if disp > 5:
			if plot:
				plot_values([va, vb, vc], [a, b, c], lastpoint=2, ftol=ftol)
		if disp > 0: print '	right %f [%f]' % (c, vc)
		if vc > vb: # finally, we found the border
			if disp > 0: print ' found right border'
			return [a, b, c], [va, vb, vc]
		if rstep < 1e-4 and c - a < 1e-4 and numpy.abs(vc - vb) < 1e-4:
			if disp > 0: print ' WARNING: hit the upper limit of the parameter', rstep, b, c, vb, vc
			return [a, b, c], [va, vb, vc]
	return [a, b, c], [va, vb, vc]

def seek_minimum_bracket(function, b, cons, ftol, disp, plot):
	# we want to bracket the minimum first
	lstep = 0.7
	rstep = 0.7
	
	assert not any([c(b) < 0 for c in cons]), [b]
	vb = function(b)
	if disp > 0: print 'starting at %f [%f]' % (b, vb)
	while any([c(b - lstep) < 0 for c in cons]):
		lstep /= 3
		if disp > 0: print 'reducing lstep for constraint'
	a = b - lstep
	va = function(a)
	if disp > 0: print 'left %f [%f]' % (a, va)
	#plot([va, vb], [a, b], lastpoint=0, ftol=ftol)
	
	if va <= vb: # we have to go left
		return escalate_left(function, a, b, va, vb, cons, lstep, ftol, disp, plot)
	
	while any([c(b + rstep) < 0 for c in cons]):
		rstep /= 3
		if disp > 0: print 'reducing rstep for constraint'
	c = b + rstep
	vc = function(c)
	#plot([va, vb, vc], [a, b, c], lastpoint=2, ftol=ftol)
	if disp > 0: print 'right %f [%f]' % (c, vc)
	
	if vc <= vb: # we have to go right
		return escalate_right(function, b, c, vb, vc, cons, rstep, ftol, disp, plot)
	return [a, b, c], [va, vb, vc]

def brent(function, a, b, c, va, vb, vc, cons, ftol, disp=0, plot=False):
	while True:
		if disp > 0: print ' BRENT', a, b, c, va, vb, vc
		if vb <= va and vb <= vc:
			if numpy.abs(vb - va) + numpy.abs(vb - vc) <= ftol:
				if disp > 0: print ' ===> found minimum at %f, %f' % (b, vb)
				return b
		if numpy.abs(vb - va) + numpy.abs(vb - vc) <= ftol:
			print 'Potentially problematic case. Increasing verbosity!'
			print '   Narrowing to ftol:', numpy.abs(vb - va) + numpy.abs(vb - vc)
			disp = 4
		x = b - 0.5 * ((b - a)**2 * (vb - vc) - (b - c)**2*(vb - va)) / ((b - a) * (vb - vc) - (b - c) * (vb - va))
		if disp > 0: print 'suggested point:', x
		safety = 10.
		if x < b and x > a and c - b >= (b - a) * safety:
			if disp > 0: print 'we want to go left, but right side is getting too mighty'
			x = (c + (safety - 1) * b) / safety
		if x < c and x > b and b - a >= (c - b) * safety:
			if disp > 0: print 'we want to go right, but left side is getting too mighty'
			x = ((safety - 1) * b + a) / safety
		
		safety2 = 10.
		if x <= b:
			if x - a <= numpy.abs(b - a) / safety2:
				if disp > 0: print 'we want to go left, but are too close to left side'
				x = a + (b - a) / safety2
			if b - x <= (b - a) / safety2:
				if disp > 0: print 'we want to go left, but are too close to the center'
				if (b - a) * numpy.abs(va - vb) >= (c - b) * numpy.abs(vc - vb) * safety**2:
					if disp > 0: print 'left side is very mighty'
					x = (b + a) / 2.
				else:
					x = b - (b - a) / safety2
		if x >= b:
			if c - x <= numpy.abs(c - b) / safety2:
				if disp > 0: print 'we want to go right, but are too close to right side'
				x = c - (c - b) / safety2
			if x - b <= (c - b) / safety2:
				if disp > 0: print 'we want to go right, but are too close to the center'
				if (c - b) * numpy.abs(vc - vb) >= (b - a) * numpy.abs(va - vb) * safety**2:
					if disp > 0: print 'right side is very mighty'
					x = (b + c) / 2.
				else:
					x = b + (c - b) / safety2
		
		if va < vb: # should go left
			if x > a:
				if disp > 0: print 'I think we should go further left, to bracket the minimum'
				(a, b, c), (va, vb, vc) = escalate_left(function, a, b, va, vb, cons=cons, lstep=c - a, ftol=ftol, disp=disp, plot=plot)
				if numpy.abs(vb - va) + numpy.abs(vb - vc) <= ftol:
					if disp > 0: print ' ===> found minimum at left border %f, %f' % (b, vb)
					return b
				#disp = 4
				continue
				x = a - (c - b)
				
		if vc < vb: # should go right
			if x < c:
				if disp > 0: print 'I think we should go further right, to bracket the minimum'
				(a, b, c), (va, vb, vc) = escalate_right(function, b, c, vb, vc, cons=cons, rstep=c - a, ftol=ftol, disp=disp, plot=plot)
				if numpy.abs(vb - va) + numpy.abs(vb - vc) <= ftol:
					if disp > 0: print ' ===> found minimum at right border %f, %f' % (b, vb)
					return b
				#disp = 4
				continue
				x = c + (b - a)
		
			
		if disp > 0: print 'next     point:', x
		v = function(x)
		if disp > 0: print 'next     value:', v
		if disp > 3:
			if plot:
				plot_values([va, vb, vc, v], [a, b, c, x], lastpoint=3, ftol=ftol)
			pause()
	
		if disp > 0: print '  deciding on next bracket'
		if v < min(va, vb, vc):
			# improvement was made.
			if x < a: # go to very left
				if disp > 0: print '  <<<< '
				a, b, c, va, vb, vc = x, a, b, v, va, vb
				continue
			elif x < b: # go to left
				if disp > 0: print '  << '
				a, b, c, va, vb, vc = a, x, b, va, v, vb
				continue
			elif x > c: # go to very right
				if disp > 0: print '  >>>> '
				a, b, c, va, vb, vc = b, c, x, vb, vc, v
				continue
			else: # go to right
				if disp > 0: print '  >> '
				a, b, c, va, vb, vc = b, x, c, vb, v, vc
				continue
		# no improvement
		if disp > 0: print ' no improvement made'
		# did we try to move to the outer edges? 
		if va < vb and x < a:
			# we tried to go very left, but hit the wall
			if disp > 0: print '  |<< '
			a, b, c, va, vb, vc = x, a, b, v, va, vb
			continue
		elif vc < vb and x > c:
			# we tried to go very right, but hit the wall
			if disp > 0: print '  >>| '
			a, b, c, va, vb, vc = b, c, x, vb, vc, v
			continue
		
		if disp > 0: print ' subdividing side'
		# go to the other side
		if not (v < va or v < vc):
			if plot:
				plot_values([va, vb, vc, v], [a, b, c, x], lastpoint=3, ftol=ftol)
			if disp > 0: print 'warning: found flat bit!'
			return b
			assert False, [v < va, v, va, v < vc, v, vc]
				
		if x < b: # on the left, go to right side
			if v > va and v < vb:
				if disp > 0: print '  . | x | sequence, going left'
				a, b, c, va, vb, vc = a, x, b, va, v, vb
			elif v > va:
				if plot:
					plot_values([va, vb, vc, v], [a, b, c, x], lastpoint=3, ftol=ftol)
				disp = 4
				if disp > 0: print 'warning: found flat bit on the right!'
				return b
			else:
				if disp > 0: print '  . | x | going right'
				a, b, c, va, vb, vc = x, b, c, v, vb, vc
			continue
		else: # on the right, go to left side
			if v > vc and v < vb:
				if disp > 0: print '  . | x | sequence, going right'
				a, b, c, va, vb, vc = b, x, c, vb, v, vc
			elif v > vc:
				if plot:
					plot_values([va, vb, vc, v], [a, b, c, x], lastpoint=3, ftol=ftol)
				disp = 4
				if disp > 0: print 'warning: found flat bit on the left!'
				return b
			else:
				if disp > 0: print '  | x | . going left'
				a, b, c, va, vb, vc = a, b, x, va, vb, v
			continue
		assert False, [a, b, c, x, va, vb, vc, v]

neval = 0

def optimize(function, x0, cons=[], ftol=0.2, disp=0, plot=False):
	"""
	**Optimization method based on Brent's method**
	
	First, a bracket (a b c) is sought that contains the minimum (b value is 
	smaller than both a or c).
	
	The bracket is then recursively halfed. Here we apply some modifications
	to ensure our suggested point is not too close to either a or c,
	because that could be problematic with the local approximation.
	Also, if the bracket does not seem to include the minimum,
	it is expanded generously in the right direction until it covers it.
	
	Thus, this function is fail safe, and will always find a local minimum.
	"""
	if disp > 0:
		print
		print '  ===== custom 1d optimization routine ==== '
		print
		print 'initial suggestion on', function, ':', x0
	points = []
	values = []
	def recordfunction(x):
		v = function(x)
		points.append(x)
		values.append(v)
		return v
	(a, b, c), (va, vb, vc) = seek_minimum_bracket(recordfunction, x0, cons=cons, ftol=ftol, disp=disp, plot=plot)
	if disp > 0:
		print '---------------------------------------------------'
		print 'found useable minimum bracker after %d evaluations:' % len(points), (a, b, c), (va, vb, vc)
	if disp > 2:
		if plot:
			plot_values(values, points, lastpoint=-1, ftol=ftol)
		pause()
	
	result = brent(recordfunction, a, b, c, va, vb, vc, cons=cons, ftol=ftol, disp=disp, plot=plot)
	if disp > 0:
		print '---------------------------------------------------'
		print 'found minimum after %d evaluations:' % len(points), result
	if disp > 1 or len(points) > 20:
		if plot:
			plot_values(values, points, lastpoint=-1, ftol=ftol)
		if disp > 2:
			pause()
	if disp > 0:
		print '---------------------------------------------------'
		print
		print '  ===== end of custom 1d optimization routine ==== '
		print
	global neval
	neval += len(points)
	return result

def cache2errors(function, cache, disp=0, ftol=0.05):
	"""
	This function will attempt to identify 1 sigma errors, assuming your
	function is a chi^2. For this, the 1-sigma is bracketed.
	
	If you were smart enough to build a cache list of [x,y] into your function,
	you can pass it here. The values bracketing 1 sigma will be used as 
	starting values.
	If no such values exist, e.g. because all values were very close to the 
	optimum (good starting values), the bracket is expanded.
	"""
	
	vals = numpy.array(sorted(cache, key=lambda x: x[0]))
	if disp > 0: print ' --- cache2errors --- ', vals
	vi = vals[:,1].min()
	def renormedfunc(x):
		y = function(x)
		cache.append([x, y])
		if disp > 1: print '    renormed:', x, y, y - (vi + 1)
		return y - (vi + 1)
	vals[:,1] -= vi + 1
	lowmask = vals[:,1] < 0
	highmask = vals[:,1] > 0
	indices = numpy.arange(len(vals))
	b, vb = vals[indices[lowmask][ 0],:]
	c, vc = vals[indices[lowmask][-1],:]
	if any(vals[:,0][highmask] < b):
		if disp > 0: print 'already have bracket'
		a, va = vals[indices[highmask][vals[:,0][highmask] < b][-1],:]
	else:
		a = b
		va = vb
		while b > -50:
			a = b - max(vals[-1,0] - vals[0,0], 1)
			va = renormedfunc(a)
			if disp > 0: print 'going further left: %.1f [%.1f] --> %.1f [%.1f]' % (b, vb, a, va)
			if va > 0:
				if disp > 0: print 'found outer part'
				break
			else:
				# need to go further
				b = a
				vb = va
	
	if disp > 0: print 'left  bracket', a, b, va, vb
	if va > 0 and vb < 0:
		leftroot = scipy.optimize.brentq(renormedfunc, a, b, rtol=ftol)
	else:
		if disp > 0: print 'WARNING: border problem found.'
		leftroot = a
	if disp > 0: print 'left  root', leftroot
	
	if any(vals[:,0][highmask] > c):
		if disp > 0: print 'already have bracket'
		d, vd = vals[indices[highmask][vals[:,0][highmask] > c][ 0],:]
	else:
		d = c
		vd = vc
		while c < 50:
			d = c + max(vals[-1,0] - vals[0,0], 1)
			vd = renormedfunc(d)
			if disp > 0: print 'going further right: %.1f [%.1f] --> %.1f [%.1f]' % (c, vc, d, vd)
			if vd > 0:
				if disp > 0: print 'found outer part'
				break
			else:
				# need to go further
				c = d
				vc = vd
	if disp > 0: print 'right bracket', c, d, vc, vd
	if vd > 0 and vc < 0:
		rightroot = scipy.optimize.brentq(renormedfunc, c, d, rtol=ftol)
	else:
		if disp > 0: print 'WARNING: border problem found.'
		rightroot = d
	if disp > 0: print 'right root', rightroot
	
	assert leftroot < rightroot

	if disp > 2:
		fullvals = numpy.array(sorted(cache, key=lambda x: x[0]))
		fullvals[:,1] -= vi + 1
		plt.figure()
		plt.plot(fullvals[:,0], fullvals[:,1], 's')
		plt.plot(vals[:,0], vals[:,1], 'o')
		plt.xlim(a, d)
		plt.ylim(min(va, vb, vc, vd), max(va, vb, vc, vd))
		ymin, ymax = plt.ylim()
		plt.vlines([leftroot, rightroot], ymin, ymax, linestyles='dotted')
		plt.savefig('cache_brent.pdf')

	return leftroot, rightroot
	
	
	
	
	
