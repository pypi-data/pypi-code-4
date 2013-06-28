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
        buckets = [[] for _ in self.positions]
        # check coverage and build each amplicon
        for readpair in reads:
            read, pos = readpair[0], int(readpair[1])
            rend_pos = len(read) + pos

            for idx, pair in enumerate(self.positions):
                start, stop = pair
                amp_len = stop - start

                front = start - pos
                back = rend_pos - stop
                if front < 0:
                    if back < 0:
                        # Read is completely inside amplicon
                        span = 1.0 + ((front + back) / float(amp_len))
                    else:
                        # Read straddles end primer
                        span = 1.0 + (front / float(amp_len))
                else:
                    if back < 0:
                        # Read straddles front primer
                        span = 1.0 + (back / float(amp_len))
                    else:
                        # Read completely overlaps amplicon
                        span = 1.0

                # clean up and add the read to the amplicon
                if span > 0.90:
                    buckets[idx].append(read)
                    break

        return buckets
