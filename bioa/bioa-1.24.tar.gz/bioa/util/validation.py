"""
========================================
Validation for reconstruction algorithms
========================================
"""

__all__ = ["hamming_distance",
           "mean_diversity",
           "shannon_entropy",
           "jensen_shannon_divergence",
           "kullback_leibler_divergence",
           "root_mean_square_deviation",
           "f_score",
           "sensitivity",
           "positive_predictive_value"]

__author__ = """Nicholas Mancuso (nick.mancuso@gmail.com)"""
#   Copyright (C) 2011-2012 by
#   Nicholas Mancuso <nick.mancuso@gmail.com>
#   Bassam Torq <basamt@gmail.com>
#   All rights reserved.
#   BSD license.

import math
import time
import itertools as itools

import bioa
import metric


def hamming_distance(str1, str2):
    """ Calculate the Hamming distance between two strings

    Parameters
    ----------
    str1 : str
        First string to use in comparison

    str2 : str
        Second string to use in comparison

    Returns
    -------
    distance : int
        The Hamming distance between strings. In other words, the number
        of character inequalities.
    """
    if len(str1) != len(str2):
        raise ValueError("Strings must be equal in length!")

    return metric.hamming(str1, str2, len(str1))


def mean_diversity(amp1, amp2, overlap, sample_size):
    """ Estimate/Compute the mean overlap diversity.

    Parameters
    ----------
    amp1 : bioa.Amplicons
        First amplicon set to use in estimation.

    amp2 : bioa.Amplicons
        Second amplicon set to use in estimation.

    overlap : int
        The amount that reads from amp1 overlap with reads in amp2.

    sample_size : int
        The amount to use in the sample for estimation.

    Returns
    -------
    mean_diversity : float
        Mean overlap diversity value from the smaple.
    """
    if not amp1 or not amp2:
        raise ValueError("Amplicons must not be empty!")

    seed = int(time.time())
    return metric.diversity(amp1, amp2, overlap, sample_size, seed)


def shannon_entropy(prob_mass_map):
    """ Calculate the entropy of the given probability mass function.

    Parameters
    ----------
    prob_mass_map : dictionary
        A dictionary mapping items to probabilities.

    Returns
    -------
    entropy : float
        The shannon entropy given the PMF.
    """
    return -sum([freq * math.log(freq, 2) for freq in \
                    prob_mass_map.values() if freq != 0])


def jensen_shannon_divergence(real, predicted):
    """ Quasi-metric for computing relative entropy
    with a midpoint. It is for computing Kullback-Leibler
    Divergence when the sets for comparison might not
    contain the same elements.

    Parameters
    ----------
    real : dict
        A dictionary mapping quasispecies to frequencies.

    predicted : dict
        the calculated dictionary mapping quasispecies to frequencies.

    Returns
    -------
    divergence : float
        The "distance" between the two distributions. Formally, the
        quality of the approximation of one distribution by the other
        distribution.
    """

    midpoint = dict(real)
    for qs, freq in predicted.items():
        if qs in midpoint:
            midpoint[qs] += freq
        else:
            midpoint[qs] = freq

    for qs, freq in midpoint.items():
        midpoint[qs] = freq / 2.0

    return 0.5 * (kullback_leibler_divergence(real, midpoint) + \
            kullback_leibler_divergence(predicted, midpoint))


def kullback_leibler_divergence(real, predicted):
    """ Relative entropy between the real frequencies and the predicted
    frequencies.

    Parameters
    ----------
    real : dict
        A dictionary mapping quasispecies to frequencies.

    predicted : dict
        the calculated dictionary mapping quasispecies to frequencies.

    Returns
    -------
    divergence : float
        The "distance" between the two distributions. Formally, the
        quality of the approximation of one distribution by the other
        distribution.
    """

    sum = 0.0
    for qs, freq_r in real.items():
        freq = predicted.get(qs, float("nan"))
        operand = math.log(freq_r / freq, 2.0) if freq_r != 0 and freq != 0 else 0
        sum += freq_r * operand

    return sum


def root_mean_square_deviation(real, predicted):
    """ Root mean square deviation. If the sets do not completely
    overlap then RMSD is calculated over the intersection.

    Parameters
    ----------
    real : dict
        A dictionary mapping quasispecies to frequencies.

    predicted : dict
        the calculated dictionary mapping quasispecies to frequencies.

    Returns
    -------
    rmsd : float
        The root mean square deviation
    """
    def _lookup(qs):
        rval = real[qs] if qs in real else 0.0
        pval = predicted[qs] if qs in predicted else 0.0
        return (rval - pval)**2.0

    inter = set(real.keys()) & set(predicted.keys())
    if len(inter) == 0:
        return float("inf")

    mean = sum(itools.imap(_lookup, inter)) / float(len(inter))
    return math.sqrt(mean)


def f_score(real, predicted):
    """ F-Score, or F1-Score is defined as:
    `2 * PPV * Senstivity / (PPV + Sensitivity)`

    It can be thought of as a weighted average of PPV and Senstivity (Precision
    and Recall).

    Parameters
    ----------
    real : dict
        A dictionary mapping quasispecies to frequencies.

    predicted : dict
        The calculated dictionary mapping quasispecies to frequencies.

    Returns
    -------
    f_score : float
        Weighted average of PPV and Senstivity (Precision and Recall).
    """
    ppv = bioa.positive_predicted_value(real, predicted)
    sen = bioa.sensitivity(real, predicted)

    _sum = float(ppv + sen)

    return (2.0 * ppv * sen) / _sum if _sum else 0.0


def sensitivity(real, predicted):
    """ Sensitivity = `|True Positives| / (|True Positives| + |False Negatives|)`

    Parameters
    ----------
    real : dict
        A dictionary mapping quasispecies to frequencies.

    predicted : dict
        The calculated dictionary mapping quasispecies to frequencies.

    Returns
    -------
    sensitivity : float
        The sensitivity.
    """
    truepos = set(predicted.keys()) & set(real.keys())
    return len(truepos) / float(len(real))


def positive_predictive_value(real, predicted):
    """ PPV = `|True Positives| / (|True Positives| + |False Positives|)`

    Parameters
    ----------
    real : dict
        A dictionary mapping quasispecies to frequencies.

    predicted : dict
        The calculated dictionary mapping quasispecies to frequencies.

    Returns
    -------
    PPV : float
        The positive predicted value
    """
    truepos = set(predicted.keys()) & set(real.keys())
    return len(truepos) / float(len(predicted))
