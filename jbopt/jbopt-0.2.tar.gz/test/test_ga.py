import os
import copy
import inspyred
import random
import numpy
import json
from joblib import delayed, Parallel, Memory
cachedir = '.cache'
if not os.path.isdir(cachedir): os.mkdir(cachedir)
mem = Memory(cachedir=cachedir, verbose=False)

from numpy import log, exp, log10, loadtxt, array, linspace, pi, sin, cos
prng = random.Random()
prng.seed(0)

nvar = 500
centers = numpy.array([prng.gauss(0.5, 0.1) for _ in range(nvar)])
widths = numpy.array([(prng.gauss(0, 0.5) + 0.01)**2 for _ in range(nvar)])
widths = numpy.array([0.01, 0.05, 0.001, 0.02, 0.1] * (nvar / 5))
#widths = numpy.array([0.1 for _ in range(nvar)])

def like(params):
	return -0.5 * (((numpy.asarray(params) - centers) / widths)**2).sum()

def print_candidate(candidate, l, args):
	params = numpy.asarray(candidate)
	print params[nvar / 2], params.mean(), params.std(), l

def eval_candidate(candidate):
	l = like(candidate)
	if numpy.isnan(l):
		return -1e300
	return l

from jbopt.independent import opt_grid
def func(par):
	params = [par[0]] * nvar
	print 'flat func:', par, '-'*20,
	l = eval_candidate(params)
	print 'likelihood', ' '*30, l
	return -l

val = opt_grid([0.5], func, [(-20, 20)], ftol=1, disp=0, compute_errors=False)
l = -func(val)
startcandidate = [float(val) for _ in range(nvar)]
seeds = [startcandidate]
json.dump([{'candidate': startcandidate, 'fitness':l}], 
	open('test_ga_values.json', 'w'), indent=4)



@inspyred.ec.utilities.memoize
@inspyred.ec.evaluators.evaluator
def fitness(candidate, args):
	l = eval_candidate(candidate)
	#print_candidate(candidate, l, args)
	return l

cutoff_store = 10
def solution_archiver(random, population, archive, args):
	psize = len(population)
	population.sort(reverse=True)
	best = population[0].fitness
	print 'BEST: ', best, 'cutoff', cutoff_store
	newarchive = []
	for c in population + archive:
		if c.fitness > best - cutoff_store and c not in newarchive:
			newarchive.append(c)
	print 'ARCHIVE: ', len(archive), len(newarchive)
	json.dump([{'candidate': [float(f) for f in c.candidate], 'fitness':c.fitness} for c in newarchive], 
		open('test_ga_values.json', 'w'), indent=4)
	return newarchive

def observer(population, num_generations, num_evaluations, args):
	population.sort(reverse=True)
	candidate = population[0]
	if num_evaluations % 1000 == 0:
		print ('{0} evaluations'.format(num_evaluations)), ' best:', 
		print_candidate(candidate.candidate, candidate.fitness, args)


bounder = inspyred.ec.Bounder(lower_bound=-20, upper_bound=20)
def generator(random, args): 
	center = random.normalvariate(0.5, 0.1)
	candidate = [random.uniform(0, 1) + center for _ in range(nvar)]
	return bounder(candidate, args)

import sys
eval_log = sys.stdout

neval = 10000

@mem.cache
def run_variants(choices):
	eval_log.write('run %s\n' % choices)
	choices = copy.copy(choices)[::-1]
	if choices.pop():
		eval_log.write('\tDEA\n')
		ea = inspyred.ec.DEA(prng)
	else:	
		eval_log.write('\tGA\n')
		ea = inspyred.ec.GA(prng)
	ea.terminator = inspyred.ec.terminators.evaluation_termination
	if choices.pop():
		eval_log.write('\tvariators: npoint\n')
		variators = [inspyred.ec.variators.n_point_crossover, inspyred.ec.variators.gaussian_mutation]
	else:
		eval_log.write('\tvariators: heuristic\n')
		variators = [inspyred.ec.variators.heuristic_crossover, inspyred.ec.variators.gaussian_mutation]
	#ea.archiver = solution_archiver
	if choices.pop():
		eval_log.write('\treplacements: steady_state\n')
		ea.replacer = inspyred.ec.replacers.steady_state_replacement
	else:
		eval_log.write('\treplacements: generational\n')
		ea.replacer = inspyred.ec.replacers.generational_replacement
	ea.observer = observer

	pop_size = 4
	if choices.pop():
		pop_size = 20
		if choices.pop():
			pop_size = 100
	elif choices.pop():
		pop_size = 50
	eval_log.write('\tpop-size: %d\n' % pop_size)

	args = dict(pop_size=pop_size, 
		bounder=bounder, generator=generator, evaluator=fitness,
		max_evaluations=neval, maximize=True, seeds=seeds)
	if choices.pop():
		args['mutation_rate'] = 0.3
		eval_log.write('\t  extra: mutation_rate: 0.3\n')
	if choices.pop():
		args['gaussian_stdev'] = 0.01
		eval_log.write('\t  extra: gaussian_stdev: 0.01\n')
	if choices.pop():
		args['num_crossover_points'] = nvar / 10
		eval_log.write('\t  extra: num_crossover_points: %d\n' % (nvar / 10))
	if choices.pop():
		args['num_elites'] = 1
		eval_log.write('\t  extra: num_elites: 1\n')
	eval_log.flush()
	prng.seed(0)
	final_pop = ea.evolve(**args)
	best = max(final_pop)
	return best

def evaluate_best(candidate, fitness):
	#print 'final candidate:', candidate

	#print 'distance:', candidate
	print 'distance:', ((numpy.array(candidate) - centers)**2).mean()
	print 'final likelihood:', fitness
	eval_log.write('\tresult: likelihood: %.1f, distance: %.3f\n' % (
		fitness, ((numpy.array(candidate) - centers)**2).mean()))
	return fitness

def run_classical():
	import scipy.optimize

	def func(params):
		return -eval_candidate(params)

	"""print 'fmin ...'
	result = scipy.optimize.fmin(func, candidate, maxfun=10000, retall=True)
	print 'fmin', result
	eval_log.write('fmin\n')
	evaluate_best(result[0], result[1])"""

	print 'cobyla ...'
	result = scipy.optimize.fmin_cobyla(func, candidate, cons=[], maxfun=neval)
	print 'cobyla', result
	eval_log.write('cobyla\n')
	evaluate_best(result, func(result))

def run_mcmc():
	import emcee
	nwalkers = 2*nvar + 2
	sampler = emcee.EnsembleSampler(nwalkers, nvar, eval_candidate)
	p0 = startcandidate
	pos, prob, state = sampler.run_mcmc(p0, neval)
	print "Mean acceptance fraction:", numpy.mean(sampler.acceptance_fraction)
	print 'pos', pos
	print 'prob', prob

def run_indep():
	candidate = copy.copy(startcandidate)
	global neval_count
	neval_count = 0
	
	def func(params):
		l = eval_candidate(params)
		global neval_count
		neval_count = neval_count + 1
		return -l

	print 'optgrid'
	candidate = opt_grid(startcandidate, func, [(-20, 20)] * nvar, 
		ftol=1, disp=0, compute_errors=False)
	l = -func(candidate)
	print 'Best after %d evaluations' % neval_count,
	print_candidate(candidate, l, {})
	evaluate_best(candidate, l)

if __name__ == '__main__':
	import sys
	eval_log = open('test_ga%s.log' % sys.argv[1], 'w')
	if sys.argv[1] == 'mcmc':
		run_mcmc()
	elif sys.argv[1] == 'classical':
		run_classical()
	elif sys.argv[1] == 'indep':
		run_indep()
	elif sys.argv[1] == 'ga':
		nchoices = 9

		prev_choices = [False for _ in range(nchoices)]
		best = run_variants(prev_choices)
		last_val = evaluate_best(best.candidate, best.fitness)
		import scipy

		while True:
			flipbits = [scipy.random.poisson(1./nchoices) for i in range(nchoices)]
			if sum(flipbits) == 0:
				continue
			choices = [not c if f else c for c, f in zip(prev_choices, flipbits)]
			#i = random.choice(range(nchoices))
			#choices[i] = not choices[i]
			eval_log.write('flipping %s\n' % (flipbits))
			best = run_variants(choices)
			val = evaluate_best(best.candidate, best.fitness)
			if val > last_val:
				eval_log.write('GOOD CHOICE! %d=%s; now at %f\n' %(i, choices[i], val))
				last_val = val
				prev_choices = choices
			else: # go back
				#choices[i] = not choices[i]
				choices = prev_choices
			eval_log.flush()



