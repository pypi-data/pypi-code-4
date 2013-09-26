import scipy
import numpy

"""
problem is:

 Rosenbrocks valley

we will compare finding the optimum
"""


n_params = 2
def like(params):
	x, y = params
	f = (1 - x)**2 + 100*(y - x**2)**2
	return -0.5 * f

def transform(cube):
	return numpy.asarray(cube) * 10 - 2

def prior(params):
	return 0

from jbopt.classic import *
from jbopt.mcmc import *
from jbopt.mn import *
from jbopt.de import *

logfile = open('test_rosen.log', 'w')
def knowledge(ret, loglikelihood, transform, prior, **args):
	if 'method' in ret:
		logfile.write('### %10s ###\n' % ret['method'])
	if 'start' in ret:
		params = transform(ret['start'])
		logfile.write('# new starting point: %s\n' % params)
		logfile.write('# value there       : %s\n' % (prior(params) + loglikelihood(params)))
	if 'maximum' in ret:
		logfile.write('# maximum a post.   : %s\n' % ret['maximum'])
	if 'median' in ret:
		logfile.write('# median estimate   : %s\n' % ret['median'])
	if 'stdev' in ret:
		logfile.write('# std estimate      : %s\n' % ret['stdev'])
	if 'chain' in ret:
		logfile.write('# chain means       : %s\n' % ret['chain'].mean(axis=0))
		logfile.write('# chain std         : %s\n' % ret['chain'].std(axis=0))
	if 'neval' in ret:
		logfile.write('# num. of eval      : %s\n' % ret['neval'])
	logfile.flush()
	return ret

if __name__ == '__main__':
	args = dict(
		loglikelihood=like, transform=transform, prior=prior,
		parameter_names = ['c%d' % i for i in range(n_params)],
		nsteps=2000,
		seed = 0,
	)
	
	for method in 'neldermead', 'cobyla', 'bobyqa', 'ralg', 'mma', 'auglag':
		print 'next method:', method
		knowledge(classical(method=method, **args), **args)
	
	ret = knowledge(onebyone(**args), **args)
	
	knowledge(onebyone(parallel=True, find_uncertainties=True, **args), **args)
	
	knowledge(de(output_basename='test_rosenbrock_de', **args), **args)

	knowledge(mcmc(output_basename='test_rosenbrock_mcmc', **args), **args)
	
	knowledge(ensemble(output_basename='test_rosenbrock_mcmc', **args), **args)
	
	knowledge(multinest(output_basename='test_rosenbrock_mn', **args), **args)

	

