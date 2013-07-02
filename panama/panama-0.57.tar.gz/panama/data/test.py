import numpy as np
import sys
import panama
import pandas
import cPickle as pickle
from sklearn import metrics
import pylab as plt
import copy
expr = pickle.load(open('/mnt/nicolo_storage/limmi/simulation/results/expr.pickle', 'r'))
snps = pickle.load(open('/mnt/nicolo_storage/limmi/simulation/results/snps.pickle', 'r'))
truth = pickle.load(open('/mnt/nicolo_storage/limmi/simulation/results/true_associations.pickle', 'r'))
cov = np.ones((expr.shape[0], 1))

conf = panama.core.ConfounderGPLVM(expr, snps, covariates=cov, population_structure=True, num_factors=10)
conf.fit()
qv, pv = conf.association_scan()
fpr, tpr, thresholds = metrics.roc_curve(truth.flatten(), -pv.flatten())
plt.figure()
plt.plot(fpr, tpr)

sys.path.append('/home/nfusi/Dropbox/research/projects/panama_old')
from panama_old.core import run
qv1, pv1 = run.PANAMA(expr, snps, n_factors=10, parallel=False)
fpr, tpr, thresholds = metrics.roc_curve(truth.flatten(), -pv1.flatten())
plt.plot(fpr, tpr)

plt.savefig('test.png')
