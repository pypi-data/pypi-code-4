#!/usr/bin/env python
from nose.tools import *
import bioa

class TestFrequencyMatrix(object):
    def test_construct_freq_matrix(self):
        """
            This tests the frequency matrix construction routine.
            It takes a list of amplicons and returns a matrix where
            amplicons are the columns and rows are the counts of
            a hypothetical variant read.

            Using the following test data the freq-matrix should be:

                F = 2 2 1
                    1 1 1
                    0 0 1

            ======================NOTICE==========================
            Since Python is row-major we use the transpose of this
            freq-matrix for easier iteration and handling.
            ======================NOTICE==========================
        """

        data = [["abab", "baba", "abab"],
                ["cgcg", "gtgt", "gtgt"],
                ["atat", "tata", "atta"]]

        # get just the frequency matrix back
        # amplicons are columns in the F-Matrix
        actual = bioa.FrequencyMatrix(data)
        expected = [[2, 1, 0],
                    [2, 1, 0],
                    [1, 1, 1]]

        for odx, column in enumerate(expected):
            for idx, row in enumerate(column):
                eq_(expected[odx][idx], actual[odx][idx], \
                        "frequency count not correct")

        # do test again but with tuples returned
        # order is not preserved with _equal_ values so this
        # test will just make sure the correct values correspond
        # to the actual strings
        actual = bioa.FrequencyMatrix(data, True)
        expected = dict([
                    ("abab", 2), ("gtgt", 2), ("atat", 1),
                    ("baba", 1), ("cgcg", 1), ("tata", 1),
                    ("", 0),     ("", 0),     ("atta", 1)])

        for odx, column in enumerate(actual):
            for idx, row in enumerate(column):
                astr, acount = actual[odx][idx]
                assert astr in expected, "unexpected string"
                eq_(expected[astr], acount, "frequency counts not correct")

    def test_construct_normalized_freq_matrix(self):
        """
        """
        data = [["abab", "baba", "abab"],
                ["cgcg", "gtgt", "gtgt"],
                ["atat", "tata", "atta"]]

        # get just the frequency matrix back
        # amplicons are columns in the F-Matrix
        actual = bioa.FrequencyMatrix.construct_normalized_freq_matrix(data, False)
        expected = [[2/3., 1/3., 0],
                    [2/3., 1/3., 0],
                    [1/3., 1/3., 1/3.]]

        for odx, column in enumerate(expected):
            for idx, row in enumerate(column):
                eq_(expected[odx][idx], actual[odx][idx], \
                        "frequency count not correct")

        data = [["abab", "baba", "abab", "abab"],
                ["cgcg", "gtgt", "gtgt"],
                ["atat", "tata", "atta"]]
        actual = bioa.FrequencyMatrix.construct_normalized_freq_matrix(data, False)
        expected = [[3/4., 1/4., 0],
                    [(2/3.0), (1/3.0), 0],
                    [(1/3.0),(1/3.0),(1/3.0)]]

        for odx, column in enumerate(expected):
            for idx, row in enumerate(column):
                eq_(expected[odx][idx], actual[odx][idx], \
                        "frequency count not correct")
