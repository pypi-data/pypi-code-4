#!/usr/bin/env python

"""Identify diagnostic residue sites in an alignment, given the gene tree.

Performs a likelihood ratio test using the likelihoods of ancestral node
character states at the root of the foreground in question vs. the full tree.

Rationale
---------

Consider a rooted tree:

          + BG
    root -|
          +-- FG

The length of the branch from the root to the LCA of the background taxon set
(BG) is 0; i.e. it's rooted at the base of BG. The branch to the LCA of the
foreground taxon set (FG) is non-zero, and FG is monophyletic.

Which residues in the sequence alignment most distinguish FG from BG?
That is, which residues are most "diagnostic" of the branch between FG and the
rest of the tree?

This program performs a maximum-likelihood estimate of the ancestral character
state posterior probabilities at FG and the root of the tree, then performs a
likelihood-ratio test to identify characters (residue positions) that show a
significant shift in probability between the base of the tree and FG.

Null hypothesis (H0):
    The character (residue) type at a given site at the root of the tree is the
    same at the base of FG. (Likelihoods of FG are specified by the root.)

Alternative hypothesis (H1):
    The character (residue) type at a given site at the root of the tree is
    independent of the type at the same site at the base of FG. (Likelihoods
    unspecified between FG and root.)

Procedure
---------

1. Using all columns, infer a tree rooted at the base of the background
   infer tree of foreground, full groups (root at base of BG)
2. For each column, calculate likelihoods of all chars at FG, root
3. LRT of FG vs. root; compare to chi-square distribution

"""
# See:
#     http://pycogent.sourceforge.net/examples/relative_rate.html
#     http://pycogent.sourceforge.net/examples/neutral_test.html
#     http://pycogent.sourceforge.net/examples/rate_heterogeneity.html

# TODO - refactor


import logging
import math
import os
import subprocess
import tempfile

from cogent import LoadSeqs, LoadTree
from cogent.evolve.models import WG01
from cogent.maths import stats

from Bio import AlignIO, Phylo


def compare_aln(fg_aln, bg_aln, usertree=None):
    """
    """
    assert len(fg_aln[0]) == len(bg_aln[0]), \
            "Alignments are not of equal width."

    # Combine alignments
    # biopython style:
    from copy import deepcopy
    full_aln = deepcopy(fg_aln)
    full_aln.extend(bg_aln)
    # cogent:
    # full_aln = fg_aln.addSeqs(bg_aln)

    # Get foreground (outgroup/ingroup) labels
    fg_labels = set([seq.id for seq in fg_aln])

    if usertree:
        # Use the user-provided tree
        assert os.path.isfile(usertree), \
                "User tree %s does not exist" % usertree
        treefname = usertree
    else:
        # ENH: check if fasttree or raxml is available
        #treefname = build_tree_raxml(full_aln, fg_labels)
        treefname = build_tree_fasttree(full_aln, fg_labels)

    # Reorient tree
    # - root at the common_ancestor of BG
    # - create another tree of just the outgroup
    _tree = Phylo.read(treefname, 'newick')

    # Validation
    fg_tips = [tip for tip in _tree.get_terminals() if tip.name in fg_labels]
    logging.info("Foreground is%s monophyletic",
            "" if _tree.is_monophyletic(fg_tips) else " NOT")
    # assert _tree.is_monophyletic(fg_labels)

    # RAxML splits the distance between BG and FG equally between branches
    # Put all that distance on FG's branch
    _tree.root_with_outgroup(_tree.clade[0], outgroup_branch_length=0.0)
    fulltreefname = treefname + '.full'
    Phylo.write(_tree, fulltreefname, 'newick')
    # FG is now the first clade at the base of the tree
    subtreefname = treefname + '.fg'
    Phylo.write(_tree.clade[0], subtreefname, 'newick')

    # __________________________________________________________
    # Get the maximum likelihood parameter estimates

    # Substitution model (should match what was used to build the tree)
    sm = WG01(with_rate=True, distribution='gamma')

    # Fix the alignments for cogent
    # Remove FASTA descriptions -- the tree doesn't have them
    # for rec in full_aln:
    #     rec.description == ''
    cog_full_fname = '_cog_full.fasta'
    AlignIO.write(full_aln, cog_full_fname, 'fasta')

    for rec in fg_aln:
        rec.description = ''
    cog_fg_fname = '_cog_fg.fasta'
    AlignIO.write(fg_aln, cog_fg_fname, 'fasta')

    # Null model: character states at root of tree
    tree = LoadTree(filename=fulltreefname)
    aln = LoadSeqs(cog_full_fname, format='fasta')

    lf0 = sm.makeLikelihoodFunction(tree)
    # Do the likelihood calculation & optimization
    lf0.setAlignment(aln)
    lf0.optimise(local=True)

    # Alternative model: character states at root of foreground
    # ENH: get the alt model w/o rerunning with a subtree?
    subtree = LoadTree(filename=subtreefname)
    subaln = LoadSeqs(cog_fg_fname, format='fasta')
    # or: 
    # subtree = tree.getSubTree(fg_labels)
    lf1 = sm.makeLikelihoodFunction(subtree)
    lf1.setAlignment(subaln)
    lf1.optimise(local=True)

    # __________________________________________________________
    # Ancestral character state posterior probabilities

    # Ancestral state reconstruction
    # pycogent.sourceforge.net/cookbook/using_likelihood_to_perform_evolutionary_analyses.html#reconstructing-ancestral-sequences
    # Posterior probs of sequence states at each node.
    # This behaves like a list where elements are column positions,
    # each a dictionary of characters-to-likelihoods
    # e.g.
    # for col in ancprobs0:
    #     print max(col.items(), key=lambda kv: kv[1])
    logging.info("Reconstructing ancestral character likelihoods")
    ancprobs0 = lf0.reconstructAncestralSeqs()['root']
    ancprobs1 = lf1.reconstructAncestralSeqs()['root']

    # __________________________________________________________
    # Likelihood ratio test

    # Retrieve the relevant parameters: log-likelihood, degrees of freedom

    # XXX I don't think this is right! see Felsenstein1981 for df definition
    # df1 = lf1.getNumFreeParams()  # ~number of tips
    # df0 = lf0.getNumFreeParams()  # ~number of tips
    # df = df1 - df0    # -71 = 20 - 91
    # logging.info("Degrees of freedom: %d (%d - %d)", df, df1, df0)
    df = 2

    hits = []
    value_of = lambda kv: kv[1]
    for idx, col0, col1 in zip(range(len(ancprobs0)), ancprobs0, ancprobs1):
        # ENH: same thing in reverse; test for loss of function
        #   i.e. use bg_char values in LRT instead of fg_char
        fg_char, L1 = max(col1.items(), key=value_of)
        bg_char, L0 = max(col0.items(), key=value_of)
        LLR = 2 * (math.log(L1) - math.log(L0))
        pvalue = stats.chisqprob(LLR, df)
        # XXX DBG
        logging.info("%s/%s %d : H0=%g, H1=%g, LLR=%g, p=%g"
                % (fg_char, bg_char, idx+1, L0, L1, LLR, pvalue))
        hits.append((fg_char, pvalue))

    # print "Likelihood ratio: %s, df=%s -> p-value: %s" % (LR, df, pvalue)
    return hits

    # -- --- --- --- --- --- --- ---
    # - --- --- --- --- --- --- --- -
    #  --- --- --- --- --- --- --- --
    # --- --- --- --- --- --- --- ---
    # Should also be possible to test for heterotachy throughout the tree this way
    # * can take sum of all char likelihoods -> site likelihood (for lrt)

    # ENH: ???
    # Allowing subsmat params to differ between branches:
    # http://pycogent.sourceforge.net/examples/scope_model_params_on_trees.html


def build_tree_fasttree(full_aln, fg_labels):
    """Build a phylogenetic tree w/ FastTree, given alignment and outgroup."""

    alnfname = '_tmp.seq'
    AlignIO.write(full_aln, alnfname, 'fasta')
    treefname = '_tmp_tree.nwk'
    subprocess.check_call("FastTree -pseudo -wag -gamma %s > %s"
                          % (alnfname, treefname),
                          shell=True)
    print "Wrote", treefname
    # TODO - root with outgroup fg_labels

    return treefname


def build_tree_raxml(full_aln, fg_labels):
    """Build a phylogenetic tree w/ RAxML, given alignment and outgroup.
    """


    from glob import glob

    # XXX replace w/ NamedTemporaryFile after initial inspection
    # with tempfile.NamedTemporaryFile() as tmpfile:
    alnfname = '_tmp.phy'
    AlignIO.write(full_aln, alnfname, 'phylip-relaxed')

    for oldfname in glob('RAxML_*.tmp'):
        os.remove(oldfname)
    # or:
    # from Bio.Phylo.Applications import RaxmlCommandline
    subprocess.check_call(['raxmlHPC',
        '-s', alnfname,
        '-o', ','.join(fg_labels),
        '-n', 'tmp',
        '-m', 'PROTGAMMAWAGF',
        '-p', '40000',
        # '-N', str(len(full_aln)),
        ])
    treefname = 'RAxML_bestTree.tmp'
    print "Wrote", treefname
    return treefname

# Alt: use PyCogent's NJ to build tree
    # Build tree from alignments
    # """Construct a tree from the combined alignments.
    # See:
    # http://pycogent.sourceforge.net/examples/maketree_from_proteinseqs.html 
    # """

#def build_tree_nj(full_aln, fg_labels):
    # from cogent import PROTEIN
    # from cogent.phylo import nj, distance
    ### Load our sequence alignment, explicitly setting the alphabet to be protein.
    ### XXX write the combined alignment to file
    # aln = LoadSeqs(filename='data/foo.fasta')
    # aln = LoadSeqs('data/abglobin_aa.phylip', interleaved=True, moltype=PROTEIN)
    # submat = WG01(with_rate=True, distribution='gamma')
    # dist = distance.EstimateDistances(aln, submodel=submat)
    # dist.run()
    # mytree = nj.nj(dist.getPairwiseDistances())
    # mytree.writeToFile('test_nj.tree', with_distances=True)

    # Biopython/PhyML way:
    # cmd = PhymlCommandline(
    #         input=alnfname,
    #         datatype='aa',
    #         model='WAG',
    #         frequencies='e',
    #         prop_invar='e',
    #         alpha='e',
    #         optimize='tl',
    #         )
    # out, err = cmd()
    # treefname = alnfname + '_phyml_tree.txt'


