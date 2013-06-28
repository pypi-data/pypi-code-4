# -*- coding: utf-8 -*-
""" Base Amplicon Class
"""

__author__ = """Nicholas Mancuso (nick.mancuso@gmail.com)"""
#   Copyright (C) 2011-2012 by
#   Nicholas Mancuso <nick.mancuso@gmail.com>
#   Bassam Tork <basamt@gmail.com>
#   All rights reserved.
#   BSD license.

import math
import itertools as itools
import logging
import random as rnd
import sys
from bisect import bisect_left, bisect_right
from multiprocessing import Pool

import bioa
import numpy
from scipy.stats import norm


class Amplicons(object):
    """ Class to represent amplicon data.

    Contains the reads along with the starting and ending positions of
    each amplicon, and the length of the reference genome covered by the
    amplicons.
    """
    MinAmpLen = 50

    def __init__(self, reads, start_end_positions, align_start, align_stop):
        """ Class to represent amplicon data.

        Contains the reads along with the starting and ending positions of
        each amplicon, and the length of the reference genome covered by the
        amplicons.

        Parameters
        ----------
        reads : (str, int)
            Tuple of the sequence and aligned starting position.

        start_end_positions : list of (int, int)
            List of (int, int) tuples indicating the starting and ending
            position for each amplicon.

        align_start : int
            Where the aligned reads begin in the reference.

        align_stop : int
            Where the aligned reads end in the reference.
        """
        if align_start >= align_stop:
            raise ValueError("Alignment start & stop positions must be valid!")

        self.se_positions = list(start_end_positions)
        start, stop = self.se_positions[0][0], self.se_positions[-1][1]
        self.span = (stop - start) / float(align_stop - align_start)
        self.min_coverage = 0.0
        self.min_overlap_diversity = 0.0
        self.min_nzoverlap_diversity = 0.0
        self.score = 0.0
        self.amplicons = self._build_amplicons(reads)

    def __str__(self):
        """ Return the str representation of the Amplicons.
        Use 'str(amplicons)'.

        Returns
        -------
        str_amplicons : str
            The string representation of the Amplicons.
        """
        return str(self.amplicons)

    def __len__(self):
        """ Return the number of amplicons in the amplicon-set.
        Use 'len(amplicons)'.

        Returns
        -------
        namplicons : int
            The number of amplicons in the amplicon-set.
        """
        return len(self.amplicons)

    def __getitem__(self, index):
        """ Return the amplicon at the given index.
        Use 'amplicons[index]'.

        Parameters
        ----------
        index : int
            The index of the amplicon to return.

        Returns
        -------
        amplicon : list
            The amplicon (list of (str, int)) in the indexed position.
        """
        if index < 0 or index >= len(self.amplicons):
            raise IndexError("Index was out of bounds!")
        return self.amplicons[index]

    def __iter__(self):
        """ Return an iterator for the amplicon-set.
        Use 'iter(amplicons)'.

        Returns
        -------
        ampiter : iterator
            An iterator of the amplicon-set.
        """
        return iter(self.amplicons)

    def next(self):
        """ Returns the next amplicon in iteration.

        Returns
        -------
        amplicon : list
            The next amplicon in iteration
        """
        return next(self.amplicons)

    @property
    def span(self):
        """ The fraction of the reference the amplicons span.
        This field is a property and should be used as 'amplicons.span'.

        Returns
        -------
        span : float
            The fraction of the reference spanned by the amplicon-set.
        """
        return self._span

    @span.setter
    def span(self, span):
        """ Set the fraction of the reference the amplicons span.
        This field is a property and should be used as 'amplicons.span = frac'.

        Parameters
        ----------
        span : float
            The fraction of the reference spanned by the amplicon-set.
        """
        if span < 0:
            raise ValueError("Span must be non-negative!")
        self._span = span

    @property
    def min_coverage(self):
        """ The minimum coverage defined by amplicon-set.
        Use like `amplicons.min_coverage`

        Returns
        -------
        min_cov : float
            The minimum coverage amount over the amplicon-set.
        """
        return self._min_coverage

    @min_coverage.setter
    def min_coverage(self, coverage):
        """ The minimum coverage defined by amplicon-set.
        Use like `amplicons.min_coverage = coverage`

        Parameters
        -------
        coverage : float
            The minimum coverage amount over the amplicon-set.
        """
        if coverage < 0:
            raise ValueError("Coverage must be non-negative!")
        self._min_coverage = coverage

    @property
    def score(self):
        """ The score of the currently defined amplicon-set
        given the read-data. Takes into account coverage and
        overlap diversity. Use like `amplicons.score`

        Returns
        -------
        score : float
            The log-score of the amplicon-set given the read-data.

        Notes
        -----
        score is not set by default. To get the actual score,
        :py:meth:`Amplicons.calc_score` must be called first.
        """
        return self._score

    @score.setter
    def score(self, score):
        """ The score of the currently defined amplicon-set given the
        read-data. Takes into account coverage and overlap diversity.
        Use like `amplicons.score = score`

        Parameters
        -------
        score : float
            The log-score of the amplicon-set given the read-data.
        """
        self._score = score

    def calc_score(self, avg_cov, std_cov, avg_div, std_div):
        """ Calculates the score of the amplicons set.

        It is the sum of the logs of the following probabilities:
            P(zscore < zscore(Min Coverage))

            P(zscore < zscore(Min Diversity))

            P(zscore < zscore(Min Non-Zero Diversity))

        Parameters
        ----------
        avg_cov : float
            Average (mean) coverage.

        std_cov : float
            Standard deviation of coverage.

        avg_div : float
            Average (mean) diversity.

        std_div : float
            Standard deviation of diversity.

        Returns
        -------
        score : float
            Score is defined as:
            log(prob_cov_zscore) + log(prob_div_zscore) + log(prob_nzdiv_score)
        """
        # calculate the CDF from the z-scores of coverage, overlap diversity
        # and, non-zero diversity. Break it up like this to avoid warning
        # messages  from divide-by-zero errors
        probs = []
        if std_cov != 0:
            probs.append(norm.cdf((self.min_coverage - avg_cov) / std_cov))
        else:
            probs.append(float('nan'))

        if std_div != 0:
            olap_zscore = (self.min_overlap_diversity - avg_div) / std_div
            nzlap_zscore = (self.min_nzoverlap_diversity - avg_div) / std_div
            probs.append(norm.cdf(olap_zscore))
            probs.append(norm.cdf(nzlap_zscore))
        else:
            probs.append(float('nan'))
            probs.append(float('nan'))

        self.score = sum(map(lambda x: math.log(max(1e-100, x)), probs))
        if math.isnan(self.score) or math.isinf(self.score):
            self.score = -1e-100

        return self.score

    @classmethod
    def is_valid(cls, starts, ends):
        """ Determins whether the given configuration is valid.

        Parameters
        ----------
        starts : list
            List of starting positions for each amplicon.

        ends : list
            List of ending positions for each amplicon.

        Returns
        -------
        is_valid : bool
            If any starting and ending position do not agree
            with their neighbors, the configuration is invalid.
        """
        if len(starts) == 1 and len(ends) == 1:
            return True

        pairs = zip(starts, ends)
        for idx, pair in enumerate(pairs[:-1]):
            start, stop = pair
            nstart, nstop = starts[idx + 1], ends[idx + 1]
            if not (start < nstart and stop < nstop and \
                    start < stop and nstart < nstop and nstart < stop):
                return False
        return True

    def get_reference_len(self):
        """ Get the length of the reference the reads are aligned to.

        Returns
        -------
        ref_len : int
            Length of the reference.
        """
        return self.ref_len

    def get_start_end_positions(self):
        """ Get the start and ending positions of the amplicons.

        Returns
        -------
        se_positions : list
            List of (int, int) tuples which corresponds to the starting
            and ending position of each amplicon.
        """
        return list(self.se_positions)

    def get_start_end_position(self, amplicon_index):
        """ Get the start and end position of the amplicon.

        Parameters
        ----------
        amplicon_index : int
            Index of the amplicon.

        Returns
        -------
        start_end_pos : (int, int)
            Start and ending position of the amplicon at amplicon_index
        """
        if amplicon_index < 0:
            raise ValueError("Amplicon ID must be non-negative!")

        return self.se_positions[amplicon_index]

    def _build_amplicons(self, reads):
        """ Build the amplicons given the reads and current configuration.
        """
        amplicons = [[] for _ in self.se_positions]
        # check coverage and build each amplicon
        for readpair in reads:
            read, pos = readpair[0], int(readpair[1])
            rend_pos = len(read) + pos

            for idx, pair in enumerate(self.se_positions):
                start, stop = pair
                amp_len = stop - start

                front = start - pos
                back = rend_pos - stop
                nread = None
                if front < 0:
                    if back < 0:
                        # Read is completely inside amplicon
                        if 1.0 + ((front + back) / float(amp_len)) > 0.90:
                            nread = ("-" * (-front)) + read
                    else:
                        # Read straddles end primer
                        if 1.0 + (front / float(amp_len)) > 0.90:
                            nread = ("-" * (-front)) + read[:stop - pos]
                else:
                    if back < 0:
                        # Read straddles front primer
                        if 1.0 + (back / float(amp_len)) > 0.90:
                            nread = read[start - pos:]
                    else:
                        # Read completely overlaps amplicon
                        nread = read[start - pos:stop - pos]

                # clean up and add the read to the amplicon
                if nread is not None:
                    # clean up and add the read to the amplicon
                    amplicons[idx].append(nread)
                    break

        self.min_coverage = min(itools.imap(len, amplicons))

        # compute diversity estimation if all amplicons are covered
        if self.min_coverage > 0:
            sample_size = 3000
            mod, mnzod = self._calculate_diversity(amplicons, sample_size)
            self.min_overlap_diversity = mod
            self.min_nzoverlap_diversity = mnzod
        else:
            self.min_overlap_diversity = 0.0
            self.min_nzoverlap_diversity = 0.0

        return amplicons

    def _calculate_diversity(self, amplicons, sample_size):
        """ Calculate the overlap diversity of the amplicons.

        Parameters
        ----------
        amplicons : bioa.Amplicons
            The amplicon set to compute diversity. It is required
            that no amplicon is empty.

        sample_size : int
            The amount to sample from neighboring amplicons when computing
            diversity.

        Returns
        -------
        min_overlap_div, min_nzoverlap_div : (float, float)
            The minimum overlap diversity and the minimum non-zero overlap
            diversity.
        """
        total = 0.0
        overlap_divs = []
        min_overlap_div = sys.maxint
        for idx, amplicon in enumerate(amplicons[:-1]):
            namplicon = amplicons[idx + 1]
            start, stop = self.se_positions[idx]
            nstart, nstop = self.se_positions[idx + 1]
            overlap = stop - nstart
            # compute the diversity in the overlap
            overlap_div = bioa.mean_diversity(amplicon, namplicon,
                                overlap, sample_size)
            total += overlap_div

            overlap_divs.append(overlap_div)
            min_overlap_div = min(min_overlap_div, overlap_div)

        min_nzoverlap_div = total / float(len(overlap_divs))

        return min_overlap_div, min_nzoverlap_div

    @classmethod
    def estimate_amplicons(cls, reads, align_start, align_stop, min_amp_len,
            iterations, threads=1):
        """ Estimate the amplicons given the read data via Monte-Carlo method.

        Parameters
        ----------
        reads : (str, int)
            Tuple of the sequence and aligned starting position.

        align_start : int
            Where the aligned reads begin in the reference.

        align_stop : int
            Where the aligned reads end in the reference.

        min_amp_len : int
            Minimum amplicon length.

        iterations : int
            How many iterations to perform in the Monte-Carlo estimation.

        threads : int, optional default=1
            The number of threads to use.

        Returns
        -------
        amplicons : bioa.Amplicons
            The randomly generated amplicons.
        """
        if not reads:
            raise ValueError("Reads must not be empty to construct amplicons!")
        if align_start < 0 or align_stop < 0 or align_start > align_stop:
            raise ValueError("Correct align start and stop values must be given!")
        if min_amp_len < 2:
            raise ValueError("Minimum amplicon length must be greater than 1!")
        if iterations < 1:
            raise ValueError("Number of iterations must be positive!")
        if threads < 1:
            raise ValueError("Thread count must be non-negative!")

        pool = Pool(threads)
        avg_len = numpy.mean(map(lambda x: len(x[0]), reads))
        std_len = numpy.std(map(lambda x: len(x[0]), reads))
        window_sizes = [(avg_len + std_len), avg_len, (avg_len - std_len), \
                        (avg_len - (2 * std_len)), (avg_len - (3 * std_len))]
        window_sizes = map(int, window_sizes)

        cls.MinAmpLen = min_amp_len
        amplicons = []
        # estimate the sliding windows
        for idx, size in enumerate(window_sizes):
            if size < cls.MinAmpLen:
                window_sizes[idx] = max(cls.MinAmpLen, rnd.random() * avg_len)

        # try stepping 20-bases at a time
        pool_params = []
        for step in (i / 20.0 for i in range(1, 20)):
            param = (reads, align_start, align_stop, window_sizes, step)
            pool_params.append(param)

        # estimate fixed overlaps
        logging.debug("Seting up sliding window amplicon estimation...")
        pool_obj = PoolAmpObj(cls)
        fixed_amps = pool.map(pool_obj, pool_params)
        for amps in fixed_amps:
            amplicons.extend(amps)
        log_str = "Built {0} putative sliding window amplicon-sets."
        log_str = log_str.format(len(amplicons))
        logging.debug(log_str)
        logging.debug("Finished sliding window amplicon estimation.")

        # estimate random overlaps
        logging.debug("Seting up random window amplicon estimation...")
        params = (reads, avg_len, std_len, align_start, align_stop)
        pool_params = itools.repeat(params, iterations)
        pool_obj = PoolRandAmpObj(cls)
        rand_amps = filter(lambda x: x is not None, pool.map(pool_obj, pool_params))
        log_str = "Built {0} putative random amplicon-sets."
        log_str = log_str.format(len(rand_amps))
        logging.debug(log_str)
        amplicons.extend(rand_amps)
        logging.debug("Finished random window amplicon estimation.")

        # select the best set
        coverages = map(lambda x: x.min_coverage, amplicons)
        diversities = map(lambda x: x.min_overlap_diversity, amplicons)
        avg_cov = numpy.mean(coverages) if coverages else 0.0
        std_cov = numpy.std(coverages) if coverages else 0.0
        avg_div = numpy.mean(diversities) if diversities else 0.0
        std_div = numpy.std(diversities) if diversities else 0.0

        # log the results
        log_str = "Mean & Std-Dev min-coverage of amplicon sets: {0}, {1}"
        log_str = log_str.format(avg_cov, std_cov)
        logging.debug(log_str)
        log_str = "Mean & Std-Dev min-diversity of amplicon sets: {0}, {1}"
        log_str = log_str.format(avg_div, std_div)
        logging.debug(log_str)

        logging.debug("Beginning amplicon score calculations...")
        for putative_amplicons in amplicons:
            putative_amplicons.calc_score(avg_cov, std_cov, avg_div, std_div)
        logging.debug("Finished amplicon score calculations.")

        best = max(amplicons, key=lambda x: x.score) if amplicons else None

        # log the final results
        if best:
            log_str = "Min-coverage of best amplicon set: {0}"
            log_str = log_str.format(best.min_coverage)
            logging.debug(log_str)
            log_str = "Min-diversity of best amplicon set: {0}"
            log_str = log_str.format(best.min_overlap_diversity)
            logging.debug(log_str)
            log_str = "Score of best amplicon set: {0}"
            log_str = log_str.format(best.score)
            logging.debug(log_str)

        return best

    @classmethod
    def amplicons_from_windows(cls, reads, align_start, align_stop,
            window_sizes, fraction):
        """ Build candidate amplicons from the defined window sizes.
        Amplicons should be uniformly distributed given a size in the list
        of allowable sizes.

        Parameters
        ----------
        reads : (str, int)
            Tuple of the sequence and aligned starting position.

        align_start : int
            Where the aligned read set begins in the reference.

        align_stop : int
            Where the aligned read set ends in the reference.

        window_sizes : list
            List of allowable amplicon sizes.

        fraction : float
            The fraction of each size in allowable sizes to try.

        Returns
        -------
        amplicon_family : list
            List of candidate amplicon-sets over the read data.
        """
        amplicons = []
        span_len = align_stop - align_start
        for win_size in window_sizes:
            step = int(math.ceil(fraction * win_size))
            num_windows = int(math.ceil(span_len / float(step)))

            if num_windows > 1:
                starts = [align_start] + ([0] * (num_windows - 1))
                stops = [align_start + win_size] + ([0] * (num_windows - 1))
                for idx, _ in enumerate(starts):
                    if idx == 0:
                        continue
                    starts[idx] = int(starts[idx - 1] + step)
                    stops[idx] = starts[idx] + win_size

                stops[-1] = align_stop
                if cls.is_valid(starts, stops):
                    amp = cls(reads, zip(starts, stops), align_start,
                            align_stop)
                    if amp.min_coverage >= 1:
                        amplicons.append(amp)
            else:
                st = int(max(2, rnd.random() * (align_stop - align_start)))
                starts = [align_start, align_stop - st]
                stops = [align_start + st, align_stop]
                # create local amplicon here and check if it is ok
                if cls.is_valid(starts, stops):
                    amp = cls(reads, zip(starts, stops), align_start,
                            align_stop)
                    if amp.min_coverage >= 1:
                        amplicons.append(amp)

        return amplicons

    @classmethod
    def random_amplicons(cls, reads, avg_len, std_len, align_start,
            align_stop):
        """ Generate amplicons from a random overlapping scheme for reads.

        Parameters
        ----------
        reads : (str, int)
            Tuple of the sequence and aligned starting position.

        avg_len : float
            Average (mean) read length.

        std_len : float
            Standard deviation of read length.

        align_start : int
            Where the aligned read set begins in the reference.

        align_stop : int
            Where the aligned read set ends in the reference.

        Returns
        -------
        amplicons : Amplicons
            The randomly generated amplicons.

        Notes
        -----
        This will return None if the randomly generated configuration is
        invalid.
        """
        def _rand_amp():
            rng = (rnd.gauss(0.0, 1.0) * std_len) + (avg_len - (3.0 * std_len))
            if rng < cls.MinAmpLen:
                rng = max(cls.MinAmpLen, rnd.random() * avg_len)
            return rng

        rnd_len = _rand_amp()
        prev_start = align_start
        prev_stop = int(min(align_start + rnd_len, align_stop))
        offset = rnd.random()
        starts, stops = [prev_start], [prev_stop]

        while True:
            # if we've hit the alignment stopping point, we're done
            if prev_stop == align_stop:
                break

            start = int(prev_start + (rnd_len * offset))
            rnd_len = _rand_amp()

            # find the next bound without exceeding alignment stopping point
            stop = int(min(max(prev_stop + std_len, start + rnd_len),
                                align_stop))
            starts.append(start)
            stops.append(stop)

            # adjust for next round
            prev_start, prev_stop = start, stop
            offset = rnd.random()

        if cls.is_valid(starts, stops):
            amplicons = cls(reads, zip(starts, stops), align_start, align_stop)
            if amplicons.min_coverage < 1:
                amplicons = None
        else:
            amplicons = None

        return amplicons

    @classmethod
    def build_uniform_amplicons(cls, reads, amplicon_len, overlap, ref_len):
        """ Generate amplicons that have uniform length and overlap. This is
            useful for simulated data.

        Parameters
        ----------
        reads : (str, int)
            Tuple of the sequence and aligned starting position.

        amplicon_len : int
            The length of each amplicon.

        overlap : int
            How much each amplicon overlaps with its neighbors.

        ref_len : int
            The length of the reference genome. Reads are assumed to span
            the entire reference.

        Returns
        -------
        amplicons : Amplicons
            The randomly generated amplicons.
        """
        if amplicon_len < 2:
            raise ValueError("Amplicon length must be at least 2!")
        if overlap < 1:
            raise ValueError("Overlap length must be at least 1!")
        if ref_len < 1:
            raise ValueError(
                    "Valid reference length must be defined " + \
                    "to build amplicons!")

        new_len = ref_len - amplicon_len
        amp_count = int(math.ceil(new_len / float(amplicon_len - overlap))) + 1
        se_positions = []

        # calculate the start and end position for each amplicon
        for idx in range(amp_count):
            start = idx * (amplicon_len - overlap)
            end = start + amplicon_len
            end = min([end, ref_len])
            se_positions.append((start, end))

        return cls(reads, se_positions, 0, ref_len)


class PoolAmpObj(object):
    """ Dummy object used for pickling (serialization) of data when using
    multiple processes to generate amplicons in parallel. It implements
    __call__ so the entire object may be passed in as a function.

    Example
    -------
    args = # some data
    pool_obj = PoolAmpObj(cls) # cls is Amplicons or some sub-class
    pool_obj(args) # returns cls.random_amplicons(*args)
    """
    def __init__(self, cls):
        self.cls = cls

    def __call__(self, args):
        return self.cls.amplicons_from_windows(*args)


class PoolRandAmpObj(object):
    """ Dummy object used for pickling (serialization) of data when using
    multiple processes to generate amplicons in parallel. It implements
    __call__ so the entire object may be passed in as a function.

    Example
    -------
    args = # some data
    pool_obj = PoolRandAmpObj(cls) # cls is Amplicons or some sub-class
    pool_obj(args) # returns cls.random_amplicons(*args)
    """
    def __init__(self, cls):
        self.cls = cls

    def __call__(self, args):
        return self.cls.random_amplicons(*args)
