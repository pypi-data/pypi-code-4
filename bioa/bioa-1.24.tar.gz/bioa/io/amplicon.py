# -*- coding: utf-8 -*-
"""
==========================================
Input/Output algorithms for bioa.Amplicons
==========================================
"""

__all__ = ["find_amplicons_by_primers",
           "parse_start_end_positions",
           "build_amplicons_from_file",
           "build_uniform_amplicons_from_file",
           "write_amplicons_to_fasta"]

__author__ = """Nicholas Mancuso (nick.mancuso@gmail.com)"""
# Copyright (C) 2011-2013 by
# Nicholas Mancuso <nick.mancuso@gmail.com>
# All rights reserved.
# BSD license.

import csv
import bioa as b
from Bio import SeqIO


def find_amplicons_by_primers(reference, primers):
    """ Finds the amplicon starting and ending positions
    in the reference given the primers used for the experiments.

    Parameters
    ----------
    reference : Bio.Seq
        The reference sequence used to align reads with.

    primers : list of Bio.SeqRecord
        List containing starting and ending primers for all
        experiments. Primers should be ordered by the amplicon order
        along the reference. Additionally each pair should be ordered
        by starting primer then ending primer.

    Returns
    -------
    se_positions : list of (int, int)
        List of integer pairs indicating the starting and ending positions
        for each amplicon in the reference.
    """
    if not reference:
        raise ValueError("Must provide a reference to find amplicons!")
    if not primers:
        raise ValueError("Must provide a primer list!")

    if len(primers) % 2 != 0:
        raise ValueError("Must be starting and ending primers for each amplicon!")

    # alignment scores
    open_gap = -0.5
    extend_gap = -0.1
    match_matrix = {("A", "A"): 2, ("A", "C"): -1, ("A", "G"): -1, ("A", "T"): -1,
              ("C", "C"): 2, ("C", "G"): -1, ("C", "T"): -1, ("G", "G"): 2,
              ("G", "T"): -1, ("W", "A"): 2, ("W", "C"): -1, ("W", "G"): -1,
              ("W", "T"): 2, ("S", "A"): -1, ("S", "C"): 2, ("S", "G"): 2,
              ("S", "T"): -1, ("M", "A"): 2, ("M", "C"): 2, ("M", "G"): -1,
              ("M", "T"): -1, ("K", "A"): -1, ("K", "C"): -1, ("K", "G"): 2,
              ("K", "T"): 2, ("R", "A"): 2, ("R", "C"): -1, ("R", "G"): 2,
              ("R", "T"): -1, ("Y", "A"): -1, ("Y", "C"): 2, ("Y", "G"): -1,
              ("Y", "T"): 2, ("B", "A"): -1, ("B", "C"): 2, ("B", "G"): 2,
              ("B", "T"): 2, ("D", "A"): 2, ("D", "C"): -1, ("D", "G"): 2,
              ("D", "T"): 2, ("H", "A"): 2, ("H", "C"): 2, ("H", "G"): -1,
              ("H", "T"): 2, ("V", "A"): 2, ("V", "C"): 2, ("V", "G"): 2,
              ("V", "T"): -1, ("T", "T"): 2}
    from Bio.pairwise2 import align
    # wrapper function to find best local alignment
    def _best(reference, seq):
        return max(align.localds(reference, seq, match_matrix,
                    open_gap, extend_gap))

    se_positions = []
    for idx in range(0, len(primers) - 1, 2):
        record = primers[idx]
        nextrecord = primers[idx + 1]
        # do a local alignment of the primers to the reference.
        s1, s2, score, begin, _ = _best(reference, record.seq)

        # reverse complement for the backward primer
        reverse = nextrecord.seq.reverse_complement()
        s1, s2, score, _, end = _best(reference, reverse)

        # account for 1-based positions in SAM/BAM files.
        se_positions.append((begin + 1, end + 1))

    return se_positions


def parse_start_end_positions(stream):
    """ Parse a stream that contains start and end positions
    for the defined amplicons. One pair per line, e.g.,
        1, 250
        183, 400
    would be the starting and ending positions for two amplicons.

    Parameters
    ----------
    stream : stream type
        The stream to parse the pairs from

    Returns
    -------
    pairs : iterable of (int, int)
        The starting and ending positions.
    """
    reader = csv.reader(stream)
    for row in reader:
        if len(row) == 2:
            yield (int(row[0]), int(row[1]))
    return


def build_amplicons_from_file(filename, se_positions, ref_len):
    """ Creates the Amplicons data structure from a file of reads.
    The file structure must follow:
        read, position
    for this to operate correctly.

    Parameters
    ----------
    filename : str
        Path to the read-data file.

    se_positions : list of (int, int)
        List of starting and ending positions for each amplicon.

    ref_len : int
        Length of the entire reference genome.

    Returns
    -------
    amplicons : bioa.Amplicons
        Amplicon data structure containing all distinct reads and meta-data.
    """

    amplicons = []
    with open(filename, "r") as data_file:
        amplicons = b.Amplicons(data_file, se_positions, ref_len)

    return amplicons


def build_uniform_amplicons_from_file(filename, amp_len, overlap, ref_len):
    """ Creates the Amplicons data structure from a file of reads.
    The file structure must follow:
            read, position
    for this to operate correctly. This assumes that all neigboring
    amplicons have the same overlap.

    Parameters
    ----------
    filename : str
        Path to the read-data file.

    amp_len : int
        Number of bases covered by a single amplicon.

    overlap : int
        The number of bases that neighboring amplicons overlap.

    ref_len : int
        Length of the entire reference genome.

    Returns
    -------
    amplicons : bioa.Amplicons
        Amplicon data structure containing all distinct reads and meta-data.
    """

    amplicons = []
    with open(filename, "r") as data_file:
        amplicons = b.Amplicons.build_uniform_amplicons(data_file, amp_len, \
                        overlap, ref_len)

    return amplicons


def write_amplicons_to_fasta(filename, amplicons):
    """ Write amplicon sequences to file.

    Parameters
    ----------
    filename : str
        Filename to write amplicon sequence data to.

    amplicons : bioa.Amplicons
        Amplicon data structure containing all distinct reads and meta-data.

    Returns
    -------
    None
    """

    with open(filename, "w") as fasta_file:
        for amplicon in amplicons:
            SeqIO.write(amplicon, fasta_file, "fasta")
    return
