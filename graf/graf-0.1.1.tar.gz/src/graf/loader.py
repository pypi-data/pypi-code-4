#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
"""
A data loader module

(C) 2013 hashnote.net, Alisue
"""
__author__ = 'Alisue (lambdalisue@hashnote.net)'
__version__ = '0.1.0'
import os
import warnings
import itertools
import numpy as np
from natsort import natsorted
from graf.utils.rglob import glob


def slice_columns(x, using=None):
    """
    Slice a numpy array to make columns

    Args:
        x: a numpy array instance
        using: a list of index or slice instance

    Returns:
        A list of columns sliced
    """
    if using is None:
        using = range(0, len(x[0]))
    return [x[:,s] for s in using]

def unite_dataset(dataset, basecolumn):
    """
    Unite dataset into a single data

    Args:
        dataset: a data list of a column list of a numpy arrays
        basecolumn: an index of base column. all data will be trimmed based on
            the order of this column when the number of samples are different
            among the dataset (Default: 0)

    Returns:
        A column list of a numpy array
    """
    ndata = [None] * len(dataset[0])
    for pdata in dataset:
        # select basecolumn
        bnx = ndata[basecolumn]
        bpx = pdata[basecolumn]
        # calculate min and max of this and final data
        if bnx is not None and len(bnx) != len(bpx):
            # the number of samples is different, so regulation is required
            xmin = max(np.min(bnx), np.min(bpx))
            xmax = min(np.max(bnx), np.max(bpx))
            # slice the data
            nindex = np.where((bnx>xmin) & (bnx<xmax))
            pindex = np.where((bpx>xmin) & (bpx<xmax))
        else:
            nindex = None
            pindex = None
        for i, (nx, px) in enumerate(itertools.izip(ndata, pdata)):
            if nindex: nx = nx[nindex]
            if pindex: px = px[pindex]
            ndata[i] = px if nx is None else np.c_[nx, px]
    return [ndata]


class BaseLoader(object):
    """
    A base loader class
    """
    def __init__(self, using=None, parser=None):
        """
        Constructor

        Args:
            using: a default list of index or slice instance
            parser: a default instance of parser class
        """
        self.using = using
        self.parser = parser

    def load(self, filename, using=None, parser=None, **kwargs):
        """
        Load data from file using a specified parser.

        Return value will be separated or sliced into a column list

        Args:
            filename: a data file path
            using: a list of index or slice instance
            parser: an instance or registered name of parser class
            **kwargs: optional arguments

        Returns:
            A list of numpy array
        """
        using = using or self.using
        parser = parser or self.parser
        # parse iterator with the specified parser
        data = parser.load(filename, **kwargs)
        # slice column by using
        return slice_columns(data, using)

    def glob(self, pathname, using=None,
             unite=False, basecolumn=0, parser=None, 
             with_filename=False, **kwargs):
        """
        Load data from file matched with given glob pattern.

        Return value will be a list of data unless `unite` is true.
        If `unite` is true, all dataset will be united into a single
        data.

        Args:
            pathname: a glob pattern
            using: a list of index or slice instance
            unite: if it is true, returning dataset will be united into a single
                data
            basecolumn: an index of base column. all data will be trimmed based on
                the order of this column when the number of samples are different
                among the dataset (Default: 0). It only affect when `unite` is
                true
            parser: an instance or registered name of parser class
            with_filename: if it is true, returning dataset will contain
                filename in the first column. it is cannot be used with
                `unite = True`
            **kwargs: optional arguments

        Returns:
            A list of numpy array or A nested list of numpy array
        """
        # argument check
        if unite and with_filename:
            raise AttributeError(
                    "`with_filename` attribute cannot be set True when "
                    "`unite` attribute was set True.")
        # make sure that the pathname is absolute
        pathname = os.path.abspath(pathname)
        # create dataset
        dataset =[]
        for filename in natsorted(glob(pathname)):
            data = self.load(
                filename=filename,
                using=using,
                parser=parser,
                **kwargs)
            if with_filename:
                data = [filename] + data
            dataset.append(data)
        # sort naturally
        if len(dataset) == 0 and not kwargs.get('quiet', False):
            warnings.warn("Nothing found with glob pattern '%s'" % pathname)
        # unite dataset if specified
        if unite and len(dataset) > 0:
            dataset = unite_dataset(dataset, basecolumn)
        return dataset
