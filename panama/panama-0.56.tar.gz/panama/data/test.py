import numpy as np
import sys
sys.path.append('./../../')
import panama3
import pandas
import cPickle as pickle
from sklearn import metrics
import pylab as plt
# from panama.core import run

expr = pickle.load(open('/mnt/nicolo_storage/limmi/simulation/results/expr.pickle', 'r'))
snps = pickle.load(open('/mnt/nicolo_storage/limmi/simulation/results/snps.pickle', 'r'))
truth = pickle.load(open('/mnt/nicolo_storage/limmi/simulation/results/true_associations.pickle', 'r'))
cov = np.ones((expr.shape[0], 1))


conf = panama.core.ConfounderGPLVM(expr, snps, covariates=cov, population_structure=None, num_factors=5)
conf.fit()
qv, pv = conf.association_scan()
fpr, tpr, thresholds = metrics.roc_curve(truth.flatten(), -pv.flatten())
plt.figure()
plt.plot(fpr, tpr)

# qv1, pv1 = run.PANAMA(expr, snps, n_factors = 5, parallel=False)
# fpr, tpr, thresholds = metrics.roc_curve(truth.flatten(), -pv1.flatten())
# plt.plot(fpr, tpr)
