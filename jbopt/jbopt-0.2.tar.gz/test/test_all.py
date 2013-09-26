import scipy
import numpy

"""
problem is:

 gaussian in 5 dimensions

problem is:

 x/y data
 find k, d, sigma-sys

"""

centers = numpy.array([0.1, 15, 3.3, 4.1, 0])
sigmas  = numpy.array([0.01, 0.1, 3, 10, 10])

def like(params):
	return -0.5 * (((params - centers) / sigmas)**2).sum()

def transform(cube):
	return numpy.asarray(cube) * 100 - 50

def prior(params):
	return 0

from jbopt.classic import *
from jbopt.mcmc import *
from jbopt.mn import *
from jbopt.de import *

logfile = open('test_all.log', 'w')
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
		parameter_names = ['c%d' % i for i in range(len(centers))],
		nsteps=2000,
		seed = 0,
	)
	
	#knowledge(classical(method='neldermead', **args), **args)
	
	#knowledge(classical(method='cobyla', **args), **args)
	for method in 'neldermead', 'cobyla', 'ralg', 'mma', 'auglag', 'minuit':
		print 'next method:', method
		knowledge(classical(method=method, **args), **args)
	
	ret = knowledge(onebyone(**args), **args)
	
	knowledge(onebyone(parallel=True, find_uncertainties=True, **args), **args)
	
	knowledge(de(output_basename='test_all_de', **args), **args)

	knowledge(mcmc(output_basename='test_all_mcmc', **args), **args)
	
	knowledge(ensemble(output_basename='test_all_mcmc', **args), **args)
	
	knowledge(multinest(output_basename='test_all_mn', **args), **args)

	

