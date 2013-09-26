"""
Classic optimization methods
"""
import numpy
from independent import opt_grid_parallel, opt_grid

def classical(transform, loglikelihood, parameter_names, prior, 
	start = 0.5, ftol=0.1, disp=0, nsteps=40000,
	method='neldermead', **args):
	"""
	**Classic optimization methods**

	:param start: start position vector (before transform)
	:param ftol: accuracy required to stop at optimum
	:param disp: verbosity
	:param nsteps: number of steps
	:param method: string
		neldermead, cobyla (via `scipy.optimize <http://docs.scipy.org/doc/scipy/reference/tutorial/optimize.html>`_)
		bobyqa, ralg, algencan, ipopt, mma, auglag and many others from the OpenOpt framework (via `openopt.NLP <http://openopt.org/NLP>`_)
		minuit (via `PyMinuit <https://code.google.com/p/pyminuit/>`_)
	"""
	import scipy.optimize
	
	n_params = len(parameter_names)
	
	def minfunc(params):
		l = loglikelihood(params)
		p = prior(params)
		if numpy.isinf(p) and p < 0:
			print '    prior rejection'
			return -1e300
		if numpy.isnan(l):
			return -1e300
		return -l - p
	def minfunc_cube(cube):
		cube = numpy.array(cube)
		if (cube <= 1e-10).any() or (cube >= 1-1e-10).any():
			return 1e100
		params = transform(cube)
		l = loglikelihood(params)
		p = prior(params)
		if numpy.isinf(p) and p < 0:
			print '    prior rejection'
			return -1e300
		if numpy.isnan(l):
			return -1e300
		return -l - p
	
	start = start + numpy.zeros(n_params)
	ret = {}
	if method == 'neldermead':
		final, value, _niter, neval, warnflag = scipy.optimize.fmin(minfunc_cube, start, ftol=ftol, disp=disp, maxfun=nsteps, full_output=True)
	elif method == 'cobyla':
		cons =  [lambda params: params[i]     for i in range(n_params)]
		cons += [lambda params: 1 - params[i] for i in range(n_params)]
		final = scipy.optimize.fmin_cobyla(minfunc_cube, start, cons, rhoend=ftol / 10, disp=disp, maxfun=nsteps)
		neval = nsteps
	elif method == 'minuit' or method == 'hesse':
		"""
		We use eval here, and it is a dangerous thing to do.
		But Minuit probes the objective function for parameter names,
		and there is no way to create the objective function 
		dynamically with an unknown number of parameters other than
		through eval.
		"""
		s = ', '.join(parameter_names)
		s = """lambda %s: minfunc([%s])""" % (s, s)
		if method == 'hesse':
			f = eval(s, dict(minfunc=minfunc, numpy=numpy))
			start = transform(start)
		else:
			f = eval(s, dict(minfunc=minfunc_cube, numpy=numpy))
		import minuit
		m = minuit.Minuit(f)
		for i, p in enumerate(parameter_names):
			m.values[p] = start[i]
			if method == 'minuit':
				m.limits[p] = (1e-10, 1 - 1e-10)
		m.up = 0.5
		m.tol = ftol * 100
		m.printMode = disp
		if method == 'minuit':
			m.migrad()
		elif method == 'hesse':
			m.hesse()
		final = [m.values[p] for p in parameter_names]
		neval = m.ncalls
		errors = [m.errors[p] for p in parameter_names]

		if method == 'minuit':
			c0 = final
			p0 = transform(c0)
			stdev = numpy.zeros(n_params)
			lower = numpy.zeros(n_params)
			upper = numpy.zeros(n_params)
			for i, w in enumerate(errors):
				c1 = numpy.copy(c0)
				c1[i] -= w
				c2 = numpy.copy(c0)
				c2[i] += w
				p1 = transform(c1)
				p2 = transform(c2)
				stdev[i] = numpy.abs(p2[i] - p1[i]) / 2
				lower[i] = min(p2[i], p1[i])
				upper[i] = max(p2[i], p1[i])
			ret['stdev'] = stdev
			ret['upper'] = upper
			ret['lower'] = lower
		elif method == 'hesse':
			ret['stdev'] = errors
			ret['cov'] = numpy.matrix([[m.covariance[(a, b)] for b in parameter_names] for a in parameter_names])
			
	else:
		from openopt import NLP
		lo = [1e-10] * n_params
		hi = [1-1e-10] * n_params
		iprint = 0 if disp == 0 else 10 if disp == 1 else 1
		p = NLP(f=minfunc_cube, x0=start, lb=lo, ub=hi,
			maxFunEvals=nsteps, ftol=ftol, iprint=iprint)
		r = p.solve(method)
		final = r.xf
		neval = r.evals['f']
	
	ret.update(dict(start=final, maximum=transform(final), method=method, neval=neval))
	return ret


def onebyone(transform, loglikelihood, parameter_names, prior, start = 0.5, ftol=0.1, disp=0, nsteps=40000,
	parallel=False, find_uncertainties=False, **args):
	"""
	**Convex optimization based on Brent's method**
	
	A strict assumption of one optimum between the parameter limits is used.
	The bounds are narrowed until it is found, i.e. the likelihood function is flat
	within the bounds.
	* If optimum outside bracket, expands bracket until contained.
	* Thus guaranteed to return local optimum.
	* Supports parallelization (multiple parameters are treated independently)
	* Supports finding ML uncertainties (Delta-Chi^2=1)

	Very useful for 1-3d problems.
	Otherwise useful, reproducible/deterministic algorithm for finding the minimum in 
	well-behaved likelihoods, where the parameters are weakly independent,
	or to find a good starting point. 
	Optimizes each parameter in order, assuming they are largely independent.
	
	For 1-dimensional algorithm used, see :func:`jbopt.opt_grid`
	
	:param ftol: difference in values at which the function can be considered flat
	:param compute_errors: compute standard deviation of gaussian around optimum
	"""
	
	def minfunc(cube):
		cube = numpy.array(cube)
		if (cube <= 1e-10).any() or (cube >= 1-1e-10).any():
			return 1e100
		params = transform(cube)
		l = loglikelihood(params)
		p = prior(params)
		if numpy.isinf(p) and p < 0:
			print '    prior rejection'
			return -1e300
		if numpy.isnan(l):
			return -1e300
		return -l - p
	
	if parallel:
		func = opt_grid_parallel
	else:
		func = opt_grid
	
	n_params = len(parameter_names)
	start = start + numpy.zeros(n_params)
	ret = func(start, minfunc, [(1e-10, 1-1e-10)] * n_params, ftol=ftol, disp=disp, compute_errors=find_uncertainties)
	
	if find_uncertainties:
		c0 = ret[0]
		p0 = transform(c0)
		stdev = numpy.zeros(n_params)
		lower = numpy.zeros(n_params)
		upper = numpy.zeros(n_params)
		for i, (lo, hi) in enumerate(ret[1]):
			c1 = numpy.copy(c0)
			c1[i] = lo
			c2 = numpy.copy(c0)
			c2[i] = hi
			p1 = transform(c1)
			p2 = transform(c2)
			stdev[i] = numpy.abs(p2[i] - p1[i]) / 2
			lower[i] = min(p2[i], p1[i])
			upper[i] = max(p2[i], p1[i])
		return dict(start=ret[0], maximum=p0,
			stdev=stdev, upper=upper, lower=lower,
			method='opt_grid')
	else:
		return dict(start=ret, maximum=transform(ret), method='opt_grid')






