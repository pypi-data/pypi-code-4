# -*- coding: utf-8 -*-
"""
================================
Grab read data from SAM/BAM file
================================
"""

__all__ = ["reads_from_sam",
           "reads_from_sam_quick"]

__author__ = "\n".join(["Nicholas Mancuso (nick.mancuso@gmail.com)",
                       "Alex Artyomenko (artyomenkoav@gmail.com)"])
#   Copyright (C) 2011-2012 by
#   Nicholas Mancuso <nick.mancuso@gmail.com>
#   Alex Artyomenko <artyomenkoav@gmail.com>
#   All rights reserved.
#   BSD license.

import sys
from collections import defaultdict

MATCH = 0
INSERTION = 1
DELETION = 2
CLIPPING = 4

INSERT_CHAR = "-"
DELETE_CHAR = "-"


def reads_from_sam_quick(sam_file):
    """ Quickly parse aligned reads from SAM/BAM file.
        This only returns reads and does not attempt
        to pad.

        Parameters
        ----------
        sam_file : pysam.SamFile
            The SAM/BAM file object.

        Returns
        -------
        read_pos_iter : (str, int) iterable
            Iterable of read-pairs indicating the read
            and its starting position in the reference.
    """
    for aligned_read in sam_file:
        if aligned_read.is_unmapped:
            continue

        yield (str(aligned_read.seq), aligned_read.pos)

    return


def reads_from_sam(sam_file, reference):
    """ Parse aligned reads from SAM/BAM file.

        Parameters
        ----------
        sam_file : pysam.SamFile
            The SAM/BAM file object.

        reference : Bio.Seq
            The reference sequence used for alignment.

        Returns
        -------
        align_start, align_stop, reads, ref : (int, int, list, Bio.Seq)
            The alignment start, alignment stop, list of reads (str, int), and
            extended reference. Each (str, int) pair represents the read and its
            starting position.
    """
    from Bio.Seq import Seq

    align_start = sys.maxint
    ref_inserts = defaultdict(int)
    for aligned_read in sam_file:
        # skip unmapped reads
        if aligned_read.is_unmapped:
            continue

        insertions = _calculate_insertions(aligned_read)
        for pos in insertions:
            ref_inserts[pos] = max(ref_inserts[pos], insertions[pos])

    # extend the reference
    new_ref = []
    for idx, nucleotide in enumerate(reference):
        new_ref.append(nucleotide)
        if idx in ref_inserts:
            new_ref.append(INSERT_CHAR * ref_inserts[idx])

    sam_file.reset()
    cache = defaultdict(int)
    align_start, align_stop, reads = _adjust_all_reads(sam_file, ref_inserts, cache)
    sam_file.close()

    return align_start, align_stop, reads, Seq("".join(new_ref))


def _adjust_all_reads(sam_file, ref_inserts, cache):
    """ Count the offset to give aligned start position.
        Adjust read and output it to ira format file.
    """
    reads = []
    align_start, align_stop = sys.maxint, 0
    for aligned_read in sam_file:
        # skip unmapped reads
        if aligned_read.is_unmapped:
            continue

        offset = _cached_pos_offset(cache, ref_inserts, aligned_read.pos)
        adj_read = _adjust_read(aligned_read, ref_inserts)
        start = aligned_read.pos + offset + 1
        align_start = min(align_start, start)
        align_stop = max(align_stop, start + len(adj_read))
        reads.append((adj_read, start))

    return align_start, align_stop, reads


def _calculate_insertions(aligned_read):
    """ Calculate the insertion positions to add to the extended reference.

        Parameters
        ----------
        aligned_read : pysam.AlignedRead
            The aligned read from a sam/bam file

        Returns
        -------
        insertions : Iterable of insertion positions
    """
    offset = 0
    ins = defaultdict(int)
    cigar = aligned_read.cigar
    pos = aligned_read.pos
    for op, count in cigar:
        if op == INSERTION:
            # output insertion positions
            ins[pos + offset - 1] = max(ins[pos + offset - 1], count)
        elif op < 2:
            # need to offset for both MATCH and INSERTION
            offset += count
    return ins


def _retrieve_insertion(new_read):
    """ Before going to insertion on cigar last insertion
        should be retrieved.
    """
    # ? What is the point of this, to remove last insertions?
    tm = new_read.pop()
    if len(tm) > 0 and tm[0] != INSERT_CHAR:
        new_read.append(tm)


def _adjust_read(aligned_read, inserts):
    """ Adjust the read to have extended characters represented by
        deleted positions.

        Parameters
        ----------
        aligned_read : pysam.AlignedRead
            The aligned read to add deletion characters to.

        inserts : dict
            Dictionary of indicies indicating an insertion in the original
            reference.

        Returns
        -------
        extended_read : Bio.Seq
            Extended sequence
    """
    # offset on reference and read
    g_offset, l_offset = 0, 0
    read = []
    for op, count in aligned_read.cigar:
        pos = aligned_read.pos
        if op == DELETION or op == MATCH:
            # append the number of deletion chars
            # append the bases, but also check if position
            # is an insertion char in the extended ref
            for i in range(count):
                char = DELETE_CHAR if op == DELETION \
                        else aligned_read.seq[i + l_offset]
                read.append(char)
                cur_pos = i + g_offset + pos
                if cur_pos in inserts and inserts[cur_pos]:
                    read.append(INSERT_CHAR * inserts[cur_pos])

            g_offset += count

        elif op == INSERTION:
            # append the insertion bases
            _retrieve_insertion(read)
            read.append(aligned_read.seq[l_offset:l_offset + count])
            ins = inserts[g_offset + pos - 1]
            if count < ins:
                read.append(INSERT_CHAR * (ins - count))

        if op == MATCH or op == INSERTION or op == CLIPPING:
            l_offset += count
        elif op == DELETION:
            l_offset -= count

    return "".join(read)


def _cached_pos_offset(cache, ref_inserts, pos):
    if pos - 1 in cache:
        return cache[pos - 1]

    val = 0
    for i in range(pos):
        val += ref_inserts[i]
        cache[i] = val

    return cache[pos - 1]
