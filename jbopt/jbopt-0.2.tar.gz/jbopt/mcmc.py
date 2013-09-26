"""
MCMC
"""
import numpy

def mcmc_advance(start, stdevs, logp, nsteps = 1e300, adapt=True, callback=None):
	"""
	Generic Metropolis MCMC. Advances the chain by nsteps.
	Called by :func:`mcmc`
	
	:param adapt: enables adaptive stepwidth alteration (converges).
	"""
	import scipy
	from numpy import log
	import progressbar
	
	prob = logp(start)
	chain = [start]
	accepts = [True]
	probs = [prob]
	assert not numpy.isnan(start).any()
	assert not numpy.isnan(stdevs).any()
	
	i = 0
	widgets=['AR', progressbar.Percentage(), progressbar.Counter('%5d'),
		progressbar.Bar(), progressbar.ETA()]
	pbar = progressbar.ProgressBar(widgets=widgets,
		maxval=nsteps).start()

	prev = start
	prev_prob = prob
	print 'MCMC: start at prob', prob
	stepchange = 0.1
	while len(chain) < nsteps:
		i = i + 1
		next = scipy.random.normal(prev, stdevs)
		next[next > 1] = 1
		next[next < 0] = 0
		next_prob = logp(next)
		assert not numpy.isnan(next).any()
		assert not numpy.isnan(next_prob).any()
		delta = next_prob - prev_prob
		dice = log(scipy.random.uniform(0, 1))
		accept = delta > dice
		if accept:
			prev = next
			prev_prob = next_prob
			if adapt: stdevs *= (1 + stepchange)
		else:
			if adapt: stdevs *= (1 + stepchange)**(-0.4) # aiming for 40% acceptance
		if callback: callback(prev_prob, prev, accept)
		chain.append(prev)
		accepts.append(accept)
		probs.append(prev_prob)
		if adapt: stepchange = min(0.1, 10. / i)
		#print 'STDEV', stdevs[:5], stepchange
		
		# compute stats
		widgets[0] = 'AR: %.03f' % numpy.mean(numpy.array(accepts[len(accepts)/3:])+0)
		pbar.update(pbar.currval + 1)
	pbar.finish()
	
	return chain, probs, accepts, stdevs

def mcmc(transform, loglikelihood, parameter_names, nsteps=40000, nburn=400, 
		stdevs=0.1, start = 0.5, **problem):
	"""
 	**Metropolis Hastings MCMC**

	with automatic step width adaption. 
	Burnin period is also used to guess steps.
	
	:param nburn: number of burnin steps
	:param stdevs: step widths to start with
	"""
	
	if 'seed' in problem:
		numpy.random.seed(problem['seed'])
	n_params = len(parameter_names)
	
	def like(cube):
		cube = numpy.array(cube)
		if (cube <= 1e-10).any() or (cube >= 1-1e-10).any():
			return -1e100
		params = transform(cube)
		return loglikelihood(params)
	
	start = start + numpy.zeros(n_params)
	stdevs = stdevs + numpy.zeros(n_params)

	def compute_stepwidths(chain):
		return numpy.std(chain, axis=0) / 3

	import matplotlib.pyplot as plt
	plt.figure(figsize=(7, 7))
	steps = numpy.array([0.1]*(n_params))
	print 'burn-in (1/2)...'
	chain, prob, _, steps_ = mcmc_advance(start, steps, like, nsteps=nburn / 2, adapt=True)
	steps = compute_stepwidths(chain)
	print 'burn-in (2/2)...'
	chain, prob, _, steps_ = mcmc_advance(chain[-1], steps, like, nsteps=nburn / 2, adapt=True)
	steps = compute_stepwidths(chain)
	print 'recording chain ...'
	chain, prob, _, steps_ = mcmc_advance(chain[-1], steps, like, nsteps=nsteps)
	chain = numpy.array(chain)

	i = numpy.argmax(prob)
	final = chain[-1]
	print 'postprocessing...'
	chain = numpy.array([transform(params) for params in chain])
	
	return dict(start=chain[-1], maximum=chain[i], seeds=[final, chain[i]], chain=chain, method='Metropolis MCMC')

def ensemble(transform, loglikelihood, parameter_names, nsteps=40000, nburn=400, 
		start=0.5, **problem):
	"""
	**Ensemble MCMC**
	
	via `emcee <http://dan.iel.fm/emcee/>`_
	"""
	import emcee
	import progressbar
	if 'seed' in problem:
		numpy.random.seed(problem['seed'])
	n_params = len(parameter_names)
	nwalkers = 50 + n_params * 2
	if nwalkers > 200:
		nwalkers = 200
	p0 = [numpy.random.rand(n_params) for i in xrange(nwalkers)]
	start = start + numpy.zeros(n_params)
	p0[0] = start

	def like(cube):
		cube = numpy.array(cube)
		if (cube <= 1e-10).any() or (cube >= 1-1e-10).any():
			return -1e100
		params = transform(cube)
		return loglikelihood(params)
	
	sampler = emcee.EnsembleSampler(nwalkers, n_params, like,
		live_dangerously=True)

	print 'burn-in...'
	pos, prob, state = sampler.run_mcmc(p0, nburn / nwalkers)

	# Reset the chain to remove the burn-in samples.
	sampler.reset()

	print 'running ...'
	# Starting from the final position in the burn-in chain, sample
	pbar = progressbar.ProgressBar(
		widgets=[progressbar.Percentage(), progressbar.Counter('%5d'),
		progressbar.Bar(), progressbar.ETA()],
		maxval=nsteps).start()
	for results in sampler.sample(pos, iterations=nsteps / nwalkers, rstate0=state):
		pbar.update(pbar.currval + 1)
	pbar.finish()

	print "Mean acceptance fraction:", numpy.mean(sampler.acceptance_fraction)

	chain = sampler.flatchain
	
	final = chain[-1]
	print 'postprocessing...'
	chain_post = numpy.array([transform(params) for params in chain])
	chain_prob = sampler.flatlnprobability
	
	return dict(start=final, chain=chain_post, chain_prior=chain,
		chain_prob=chain_prob,
		method='Ensemble MCMC')


