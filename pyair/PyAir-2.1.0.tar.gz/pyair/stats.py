#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
**Statistics

"""


import numpy as np
import numpy.ma as ma
import scipy.stats as stats



def find(condition):
    """Best finding method than matplotlib for timeseries datas
    """

    return np.ravel(np.nonzero(condition))


def to_quantile(a, nb=5):
    """Returns the nb quantiles of the list a
    """
    ind = np.linspace(0, 100, nb)
    b = a.compressed()
    return [stats.scoreatpercentile(b, i) for i in ind]


def mean(a, rep=0.75, **kwargs):
    """Compute the average along a 1D array like ma.mean,
    but with a representativity coefficient : if ma.count(a)/ma.size(a)>=rep,
    then the result is a masked value
    """
    return rfunc(a, ma.mean, rep, **kwargs)


def max(a, rep=0.75, **kwargs):
    """Compute the max along a 1D array like ma.mean,
    but with a representativity coefficient : if ma.count(a)/ma.size(a)>=rep,
    then the result is a masked value
    """
    return rfunc(a, ma.max, rep, **kwargs)


def min(a, rep=0.75, **kwargs):
    """Compute the min along a 1D array like ma.mean,
    but with a representativity coefficient : if ma.count(a)/ma.size(a)>=rep,
    then the result is a masked value
    """
    return rfunc(a, ma.min, rep, **kwargs)


def rfunc(a, rfunc=None, rep=0.75, **kwargs):
    """Applies func on a if a comes with a representativity coefficient rep,
    i.e. ma.count(a)/ma.size(a)>=rep. If not, returns a masked array
    """
    if float(ma.count(a)) / ma.size(a) < rep:
        return ma.masked
    else:
        if rfunc is None:
            return a
        return rfunc(a, **kwargs)


def bias(a, b):
    """Returns the bias between a and b
    """
    return np.mean(a - b)


def stderr(a, b):
    """Returns the standard deviation of the errors between a and b
    """
    return np.std(a - b)


def mae(a, b):
    """Returns the mean absolute error of a and b
    """
    return np.absolute(a - b).mean()


def rmse(a, b):
    """Returns the root mean square error betwwen a and b
    """
    return np.sqrt(np.square(a - b).mean())


def nmse(a, b):
    """Returns the normalized mean square error of a and b
    """
    return np.square(a - b).mean() / (a.mean()*b.mean())


def mfbe(a, b):
    """Returns the mean fractionalized bias error
    """
    return 2 * bias(a, b) / (a.mean() + b.mean())


def fa(a, b, alpha=2):
    """Returns the factor of 'alpha' (2 or 5 normally)
    """
    return np.sum((a > b / alpha) & (a < b * alpha), dtype=float) / len(a) * 100


def foex(a, b):
    """Returns the factor of exceedance
    """
    return (np.sum(a > b, dtype=float) / len(a) - 0.5) * 100


def correlation(a, b):
    """Computes the correlation between a and b, says the Pearson's correlation
    coefficient R
    """
    diff1 = a - a.mean()
    diff2 = b - b.mean()
    return (diff1 * diff2).mean() / (np.sqrt(np.square(diff1).mean() * np.square(diff2).mean()))


def determination(a, b):
    """Returns the coefficient of determination between a and b
    """
    return np.square(correlation(a, b))


def gmb(a, b):
    """Geometric mean bias
    """
    return np.exp(np.log(a).mean() - np.log(b).mean())


def gmv(a, b):
    """Geometric mean variance
    """
    return np.exp(np.square(np.log(a) - np.log(b)).mean())


def fmt(a, b):
    """Figure of merit in time
    """
    return 100 * np.min([a, b], axis=0).sum() / np.max([a, b], axis=0).sum()


def fullStats(a, b, liba, libb):
    """Performs several stats on a against b, typically a is the predictions
    array, and b the observations array
    laba and labb are the desired labels for the resulting presentation
    Returns a recarray where:
    rec.name : name of the stat
    rec.desc : sort description of the stat
    rec.result : the resulting value
    """
    #We remove all masked (invalids) datas
    a, b = lutils.dissolveMask(a, b)
    a = a.compressed()
    b = b.compressed()
    stats = list([['max', 'Max for %s' % liba, a.max()],
                      ['mean', 'Mean for %s' % liba, a.mean()],
                      ['var', 'Variance for %s' % liba, a.var()],
                      ['max', 'Max for %s' % libb, b.max()],
                      ['mean', 'Mean for %s' % libb, b.mean()],
                      ['var', 'Variance for %s' % libb, b.var()],
                      ['bias', 'Bias', bias(a, b)],
                      ['stderr', 'Standard Diviation Error', stderr(a, b)],
                      ['mae', 'Mean Absolute Error', mae(a, b)],
                      ['rmse', 'Root Mean Square Error', rmse(a, b) ],
                      ['nmse', 'Normalized Mean Square Error', nmse(a, b)],
                      ['mfbe', 'Mean Fractionalized bias Error', mfbe(a, b)],
                      ['fa2', 'Factor of Two', fa(a, b, 2)],
                      ['foex', 'Factor of Exceedance', foex(a, b)],
                      ['correlation', 'Correlation R', correlation(a, b)],
                      ['determination', 'Coefficient of Determination r2', determination(a, b)],
                      ['gmb', 'Geometric Mean Bias', gmb(a, b)],
                      ['gmv', 'Geometric Mean Variance', gmv(a, b)],
                      ['fms', 'Figure of Merit in Time', fmt(a, b)]])
    return stats


