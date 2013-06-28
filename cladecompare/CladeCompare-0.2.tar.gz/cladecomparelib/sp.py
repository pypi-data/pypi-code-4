"""Sum of pairs (SP) score.

Sum of the scores of all residue pairs between the two sets.
"""
# alignment: goal is to maximize SP score across the whole MSA.
# here: goal is to gauge difference in composition.

from Bio.SubsMat.MatrixInfo import blosum62
from biofrills import consensus, alnutils

from .shared import count_col


def compare_one(col, cons_aa, aln_size, weights, aa_freqs):
    """SP score within each column of the alignment."""
    # TODO - use sequence_weights(aln, 'sum1') in cladecompare.py as with jsd
    # weights = alnutils.sequence_weights(aln, 'sum1')

    pvalue = None
    return pvalue


def compare_one(col, cons_aa, aln_size, weights, aa_freqs):
    "Column probability using the ball-in-urn model."
    # TODO

    pvalue = None
    return pvalue
