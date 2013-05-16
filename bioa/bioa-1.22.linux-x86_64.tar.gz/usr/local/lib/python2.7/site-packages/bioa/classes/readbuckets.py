# -*- coding: utf-8 -*-
""" Read Buckets class.
"""

__author__ = """Nicholas Mancuso (nick.mancuso@gmail.com)"""
#   Copyright (C) 2011-2013 by
#   Nicholas Mancuso <nick.mancuso@gmail.com>
#   All rights reserved.
#   BSD license.
from bisect import bisect_left, bisect_right


class ReadBuckets(object):
    """ Class to represent "loose" amplicon data. This just partitions
    reads into amplicons but doesn't clip them for alignment. It can be
    thought of as a proto-Amplicons class.
    """

    def __init__(self, reads, start_end_positions):
        """
        """
        self.positions = list(start_end_positions)
        self.buckets = self._build_buckets(reads)

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
        if index < 0 or index >= len(self.buckets):
            raise IndexError("Index was out of bounds!")
        return self.buckets[index]

    def __iter__(self):
        """ Return an iterator for the amplicon-set.
        Use 'iter(readbuckets)'.

        Returns
        -------
        iter : iterator
            An iterator of the buckets.
        """
        return iter(self.buckets)

    def next(self):
        """ Returns the next amplicon in iteration.

        Returns
        -------
        amplicon : list
            The next amplicon in iteration
        """
        return next(self.buckets)

    def _build_buckets(self, reads):
        """
        """
        BAD_POS = -1
        starts, ends = zip(*self.positions)

        # use these functions to binary search the relevant amplicons
        # finds first good amplicon
        def _first(start):
            i = bisect_left(starts, start)
            if i != len(starts):
                return i
            else:
                return BAD_POS

        # finds last good amplicon
        def _last(end):
            i = bisect_right(ends, end)
            if i:
                return i - 1
            else:
                return BAD_POS

        buckets = [[] for _ in self.positions]
        # check coverage and build each amplicon
        for readpair in reads:
            read, pos = readpair[0], int(readpair[1])
            rend_pos = len(read) + pos

            # use binary search to find intervals instead of checking all
            range_start = _first(pos)
            range_stop = _last(rend_pos)

            # read cant fit anywhere
            if range_start == BAD_POS or range_stop == BAD_POS:
                continue

            for idx in range(range_start, range_stop + 1):
                start, stop = self.positions[idx]
                # clean up and add the read to the amplicon
                buckets[idx].append(read)

        return buckets
