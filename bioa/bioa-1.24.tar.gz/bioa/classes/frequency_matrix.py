# -*- coding: utf-8 -*-
""" Base FreqMatrix class.
"""
import numpy
from collections import Counter


class FrequencyMatrix(object):

    def __init__(self, amplicons, include_pairs=False, nthreads=1):
        """ This will construct the frequency matrix based on the amplicons in
            the amplicons. Columns correspond to the absolute frequency
            (i.e. counts) distributions of distinct reads in the amplicons and
            rows correspond to distinct read-representatives with their
            associated frequencies.

            Parameters
            ----------
            amplicons : list
               List of amplicons where each amplicon is a list of reads. This will
               be used to construct the frequency matrix.

            include_pairs : bool (optional, default=False)
                Whether or not to output the tuple (read, count) for each item in
                the frequency matrix rather than just count.
        """

        freqs = []
        if include_pairs:
            d_type = tuple
            fill_v = ("", 0)
        else:
            d_type = float
            fill_v = 0

        # dont use pools for this. it is fast enough sequentially.
        # trying to construct in parallel with pool causes too much
        # memory overhead
        map_func = lambda x: self._get_normalized_amps(*x)
        args = ((idx, amp, include_pairs) for idx, amp in enumerate(amplicons))
        # keep track of indx to properly place back
        freqs = sorted(map(map_func, args), key=lambda x: x[0])
        freqs = [x[1] for x in freqs]


        # get maximum read count over the amplicons
        max_read_count = len(max(freqs, key=len))
        amplicon_count = len(amplicons)

        # create a zeroed out matrix
        self.freq_matrix = numpy.zeros((amplicon_count, max_read_count), \
                                dtype=d_type)
        self.freq_matrix.fill(fill_v)

        # fill with the read frequencies
        for idx, freq_ary in enumerate(freqs):
            self.freq_matrix[idx][:len(freq_ary)] = freq_ary

    def __iter__(self):
        """ Return an iterator over the matrix.

        Returns
        ------
        iter : iterator
        """
        return iter(self.freq_matrix)

    def __len__(self):
        """ Return the column-width of the matrix

        Returns
        -------
        length : int
        """
        return len(self.freq_matrix)

    def __getitem__(self, idx):
        """ Returns a column based on the index given.

        Parameters
        ----------
        idx : int

        Returns
        -------
        column : numpy.array
            The column of frequencies for the given index.
        """
        return self.freq_matrix[idx]

    @property
    def shape(self):
        """ The shape of the frequency matrix.

        Returns
        -------
        shape : (int, int)
            The shape of the matrix
        """
        return self.freq_matrix.shape

    @classmethod
    def construct_normalized_freq_matrix(cls, amplicons, include_pairs=True, nthreads=1):
        """ This will normalize the frequencies in our matrix. Meaning that the sum
            of frequiences in each amplicon will equal one another. This is done in
            a left to right fashion by simply scaling according to the ratio of
            sums.

            Parameters
            ----------

            amplicons : list
               List of amplicons where each amplicon is a list of reads. This will
               be used to construct the frequency matrix.

            include_pairs : bool (optional, default=False)
                Whether or not to output the tuple (read, count) for each item in
                the frequency matrix rather than just count.

            nthreads : int (optional, default=1)
                The number of threads to use when counting reads per amplicon.
                Default value is single thread.

            Returns
            -------
            freq_matrix : Numpy matrix
                Frequency matrix where columns correspond to the normalized frequency
                (i.e. percentage) distributions of distinct reads in the amplicons and
                rows correspond to distinct read-representatives with their
                associated frequencies.
        """

        freq_matrix = cls(amplicons, include_pairs, nthreads)

        for idx, amplicon in enumerate(freq_matrix):
            if include_pairs:
                reads, freqs = zip(*amplicon)
            else:
                freqs = amplicon

            a_sum = float(sum(freqs))
            assert a_sum > 0, "Cannot have empty amplicon!"

            for ndx, freq in enumerate(freqs):
                val = freq / a_sum
                tmp = freq_matrix[idx][ndx]
                freq_matrix[idx][ndx] = (tmp[0], val) if include_pairs else val

        return freq_matrix

    def _get_normalized_amps(self, aid, amplicon, include_pairs):
        """
        """
        # count the number of reads over this amplicon
        read_to_count = Counter(amplicon)
        # sort by decreasing order
        if include_pairs:
            read_counts = read_to_count.items() if include_pairs else \
                    read_to_count.values()
            read_counts.sort(key=lambda x: x[1], reverse=True)
        else:
            read_counts = read_to_count.values()
            read_counts.sort(reverse=True)

        return (aid, read_counts)


class FreqMatrixPoolObj(object):

    def __init__(self, freqm):
        self.freqm = freqm
        pass

    def __call__(self, amplicon):
        return self.freqm._get_normalized_amps(*amplicon)
