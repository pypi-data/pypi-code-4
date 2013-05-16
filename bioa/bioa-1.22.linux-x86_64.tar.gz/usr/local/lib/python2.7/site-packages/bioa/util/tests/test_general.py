#!/usr/bin/env python
from nose.tools import *
import bioa

class TestGeneralUtil:

    def test_are_consistent(self):
        str1 = "zzzzabcd"
        str2 = "abcdzzzz"
        overlap = 4
        ok_(bioa.are_consistent(str1, str2, overlap),
                "strings are not consistent!")

        str1 = "zzzzabcd"
        str2 = "abcezzzz"
        overlap = 4
        ok_(not bioa.are_consistent(str1, str2, overlap),
                "strings should not be consistent!")

        str1 = "zzzzabcd"
        str2 = "abcdzzzz"
        overlap = 4
        threshold = 0.0
        ok_(bioa.are_consistent(str1, str2, overlap, threshold),
                "strings are not consistent within threshold!")

        str1 = "zzzzabff"
        str2 = "abcdzzzz"
        overlap = 4
        threshold = 2
        ok_(bioa.are_consistent(str1, str2, overlap, threshold),
                "strings are not consistent within threshold!")

        str1 = "zzzzabff"
        str2 = "abcdzzzz"
        overlap = 4
        threshold = 1
        ok_(not bioa.are_consistent(str1, str2, overlap, threshold),
                "strings should not be consistent within threshold!")

    def test_reconstruct_sequence(self):
        reads = ['abac', 'cgcg', 'gtat']
        overlap = [(0, 4), (3, 7), (6, 10)]
        expected = 'abacgcgtat'
        actual = bioa.reconstruct_sequence(reads, overlap)
        eq_(actual, expected, 'reconstructed sequence not equivalent')
