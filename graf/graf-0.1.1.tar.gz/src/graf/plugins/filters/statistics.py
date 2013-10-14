#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
"""
Statistics related functions

(C) 2013 hashnote.net, Alisue
"""
__author__ = 'Alisue (lambdalisue@hashnote.net)'
__version__ = '0.1.0'
import numpy as np

def average(x):
    """
    Return a numpy array of column average.
    It does not affect if the array is one dimension

    Example:
        >>> a = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        >>> average(a)
        array([2, 5, 8])
        >>> a = np.array([1, 2, 3])
        >>> average(a)
        array([1, 2, 3])
    """
    if x.ndim > 1 and len(x[0]) > 1:
        return np.average(x, axis=1)
    return x

def mean(x):
    """
    Return a numpy array of column mean.
    It does not affect if the array is one dimension

    Example:
        >>> a = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        >>> mean(a)
        array([2, 5, 8])
        >>> a = np.array([1, 2, 3])
        >>> mean(a)
        array([1, 2, 3])
    """
    if x.ndim > 1 and len(x[0]) > 1:
        return np.mean(x, axis=1)
    return x

def median(x):
    """
    Return a numpy array of column median.
    It does not affect if the array is one dimension

    Example:
        >>> a = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        >>> mean(a)
        array([2, 5, 8])
        >>> a = np.array([1, 2, 3])
        >>> median(a)
        array([1, 2, 3])
    """
    if x.ndim > 1 and len(x[0]) > 1:
        return np.median(x, axis=1)
    return x

def variance(x):
    """
    Return a numpy array of column variance
    """
    return np.var(x, axis=1)

def standard_deviation(x):
    """
    Return a numpy array of column standard deviation
    """
    return np.std(x, axis=1)

def confidential_interval(x, alpha=0.98):
    """
    Return a numpy array of column confidential interval

    Args:
        x: a numpy array
        alpha: alpha value of confidential interval

    Returns:
        A numpy array which indicate the each difference from sample average
        point to confidential interval point
    """
    from scipy.stats import t
    if x.ndim == 1:
        return None
    # calculate degree of freedom
    df = len(x[0]) - 1
    # calculate positive critical value of student's T distribution
    cv = t.interval(alpha, df)[1]
    # calculate sample standard distribution
    std = np.std(x, axis=1)
    # calculate positive difference from
    # sample average to confidential interval
    return std * cv / np.sqrt(df)


def __plugin__(registry):
    from graf.utils.bunch import Bunch
    statistics = Bunch(
            avg=average,
            average=average,
            mean=mean,
            median=median,
            var=variance,
            variance=variance,
            std=standard_deviation,
            standard_deviation=standard_deviation,
            interval=confidential_interval,
            confidential_interval=confidential_interval,
        )
    registry.register('filters.statistics', statistics)
__plugin__.manually = True
