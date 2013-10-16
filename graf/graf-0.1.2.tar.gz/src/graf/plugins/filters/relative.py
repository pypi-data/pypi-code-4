#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
"""
Dataset filter functions

(C) 2013 hashnote.net, Alisue
"""
__author__ = 'Alisue (lambdalisue@hashnote.net)'
__version__ = '0.1.0'
import numpy as np


def relative(dataset, ori=0, column=1):
    """
    Convert dataset to relative value from the value of ori

    Args:
        dataset: a list of numpy array
        ori: a relative original data index or numpy array
        baseecolumn: an index of base column to calculate the relative value
    """
    if isinstance(ori, int):
        # relative from the [ori]th array
        ori = dataset[ori][column]
    # calculate min/max difference
    if ori.ndim > 1 and len(ori[0]) > 1:
        ori = np.average(ori, axis=1)
    orimin = np.min(ori)
    orimax = np.max(ori)
    oridiff = orimax - orimin
    # convert
    for data in dataset:
        data[column] /= oridiff / 100.0
    return dataset

def __plugin__(registry):
    registry.register('filters.rel', relative)
    registry.register('filters.relative', relative)
__plugin__.manually = True
