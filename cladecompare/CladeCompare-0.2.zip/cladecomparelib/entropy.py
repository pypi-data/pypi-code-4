"""Take the difference of entropies between columns of two alignments.

Single mode: compare to max entropy, log(20)

"""

import logging

from biofrills import consensus, alnutils

from .shared import count_col, combined_frequencies, entropy, MAX_ENTROPY


def compare_one(fg_aln):
    """Info content: Max minus observed entropy.

    The decrease in uncertainty (entropy) from no knownledge of the column
    composition (max entropy given an alphabet of size N) to the observed column
    composition.

    Formula, via WebLogo:

    R_{seq} = S_{max} - S_{obs}
            = \log_2 N - \left( -\sum_{n=1}^{N} p_n \log_2 p_n \right)
    """
    weights = alnutils.sequence_weights(fg_aln, 'sum1')
    allfreqs = alnutils.aa_frequencies(fg_aln, weights, gap_chars='-.X')
    hits = []
    for col in zip(*fg_aln):

        col_cnts = count_col(col, weights)
        if not col_cnts:
            logging.warn("Column is all gaps; skipping")
            return 0
        S_obs = entropy(col_cnts.values())
        # Scale down for gaps & ambiguous chars
        # i.e. if XX% of col is non-gap chars, info *= 0.XX
        hits.append(
            (MAX_ENTROPY - S_obs) * (sum(col_cnts.values()) / len(col)))

    return hits


def compare_aln(fg_aln, bg_aln):
    fg_weights = alnutils.sequence_weights(fg_aln, 'sum1')
    bg_weights = alnutils.sequence_weights(bg_aln, 'sum1')
    aa_freqs = alnutils.aa_frequencies(fg_aln._records + bg_aln._records,
                                       gap_chars='-.X',
                                       weights=fg_weights + bg_weights)
    fg_cons = consensus.consensus(fg_aln, weights=fg_weights, trim_ends=False,
                                  gap_threshold=0.8)
    bg_cons = consensus.consensus(bg_aln, weights=bg_weights, trim_ends=False,
                                  gap_threshold=0.8)
    fg_cols = zip(*fg_aln)
    bg_cols = zip(*bg_aln)
    hits = []
    for faa, baa, fg_col, bg_col in zip(fg_cons, bg_cons, fg_cols, bg_cols):
        if faa == '-' or baa == '-':
            # Ignore indel columns -- there are better ways to look at these
            pvalue = 1.
        else:
            fg_entropy = entropy(count_col(fg_col, fg_weights).values())
            bg_entropy = entropy(count_col(bg_col, bg_weights).values())
            # XXX what's the probability?
            # TAMO
            pvalue = bg_entropy - fg_entropy
        hits.append((faa, baa, pvalue))

    return hits

