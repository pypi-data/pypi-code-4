#!/usr/bin/env python
# -*- coding: utf-8 -*-

from operator import itemgetter
from collections import namedtuple

from Bio.SeqUtils import GC
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from pydna import Anneal
from pydna.amplify import tmbresluc, basictm, tmstaluc98, tmbreslauer86

def cloning_primers(template,
                    minlength=16,
                    maxlength=29,
                    fp=None,
                    rp=None,
                    fp_tail='',
                    rp_tail='',
                    target_tm=55.0, 
                    primerc = 1000.0,
                    saltc=50.0,
                    formula= tmbresluc ):
                    
    '''This function can design one or two primers for PCR amplification of a 
    given sequence. This function accepts a Dseqrecord object containing the 
    template sequence and returns a pydna amplicon object.
    
    The amplicon object contains the primers, a figure describing the how the 
    primers anneal and two suggested PCR programmes.
    

    Parameters
    ----------

    template : Dseqrecord
        a Dseqrecord object.
        
    minlength : int, optional
        Minimum length of the annealing part of the primer
    
    maxlength : int, optional
        Maximum length (including tail) for designed primers.
        
    fp, rp : SeqRecord, optional
        optional Biopython SeqRecord objects containing one primer each.

    fp_tail, rp_tail : string, optional
        optional tails to be added to the forwars or reverse primers
        
    target_tm : float, optional
        target tm for the primers        

    primerc, saltc  : float, optional
        limit is set to 25 by default.

    formula : string
        formula used for tm calculation
        this is the name of a function.
        built in options are:
        
        tmbresluc
        basictm
        tmstaluc98 
        tmbreslauer86
        
    These functions are imported from the pydna.amplify module, but can be 
    substituted for some other custom made function.

    Returns
    -------
    frecs, cp : tuple
        frecs are the same Dseqrecords as given as arguments, but with the
        regions of homology added to the features.

        cp is a list of Dseqrecords representing the circular products
        sorted by length (long -> short).

        '''


    prim = namedtuple('prim', 'tm primer direction')

    if fp and not rp:
        fp = SeqRecord(Seq(fp_tail)) + fp
        p  = Anneal([fp], template).fwd_primers.pop()
        fp = SeqRecord(p.footprint)
        fp_tail = SeqRecord(p.tail.lower())
        rp = SeqRecord(Seq(str(template[-(maxlength*3-len(rp_tail)):].reverse_complement().seq)))
    elif not fp and rp:
        rp = SeqRecord(Seq(rp_tail)) + rp
        p =  Anneal([rp], template).rev_primers.pop()
        rp = SeqRecord(p.footprint)
        rp_tail = SeqRecord(p.tail.lower())
        fp = SeqRecord(Seq(str(template[:maxlength*3-len(fp_tail)].seq)))
    elif not fp and not rp:
        fp = SeqRecord(Seq(str(template[:maxlength-len(fp_tail)].seq)))
        rp = SeqRecord(Seq(str(template[-(maxlength-len(rp_tail)):].reverse_complement().seq)))
    else:
        raise Exception("not both primers!")

    lowtm, hightm = sorted( (prim( tm=formula(fp.seq.tostring(), primerc=primerc, saltc=saltc), primer=fp, direction="f"),
                             prim( tm=formula(rp.seq.tostring(), primerc=primerc, saltc=saltc), primer=rp, direction="r"),) )
    
    while lowtm.tm > target_tm and len(lowtm.primer)>minlength:
        shorter = lowtm.primer[:-1]
        tm      = formula(shorter.seq.tostring(), primerc=primerc, saltc=saltc)
        lowtm   = prim(tm, primer=shorter, direction=lowtm.direction)
        
    while hightm.tm > lowtm.tm + 2.0 and len(hightm.primer)>minlength:
        shorter = hightm.primer[:-1]
        tm = formula(shorter.seq.tostring(), primerc = primerc, saltc = saltc)
        hightm = prim(tm, primer=shorter, direction=hightm.direction)

    fp, rp = sorted((lowtm, hightm),key=itemgetter(2))
    
    limit = min(len(fp.primer),len(rp.primer))

    fp = fp_tail + fp.primer

    rp = rp_tail + rp.primer

    fp.description = ""
    rp.description = ""
    fp.id = "{}_fw".format(template.description)
    rp.id = "{}_rv".format(template.description)
    fp.name = fp.description
    rp.name = rp.description

    ann = Anneal((fp, rp), template, homology_limit = limit ).amplicons.pop()

    assert str(template.seq) in ann.pcr_product()

    return ann

if __name__=="__main__":
    
    from pygenome import sc
    sgd = sc.sc()
    from pydna import Dseqrecord
    from pydna_helper.load_my_primers import primer
    from pydna_helper import gb, ape
    
    ftail = "ttaaat"
    rtail = "taattaa"

    xdh = Dseqrecord("atgactgctaacccttccttggtgttgaacaagatcgacgacatttcgttcgaaacttacgatgccccagaaatctctgaacctaccgatgtcctcgtccaggtcaagaaaaccggtatctgtggttccgacatccacttctacgcccatggtagaatcggtaacttcgttttgaccaagccaatggtcttgggtcacgaatccgccggtactgttgtccaggttggtaagggtgtcacctctcttaaggttggtgacaacgtcgctatcgaaccaggtattccatccagattctccgacgaatacaagagcggtcactacaacttgtgtcctcacatggccttcgccgctactcctaactccaaggaaggcgaaccaaacccaccaggtaccttatgtaagtacttcaagtcgccagaagacttcttggtcaagttgccagaccacgtcagcttggaactcggtgctcttgttgagccattgtctgttggtgtccacgcctccaagttgggttccgttgctttcggcgactacgttgccgtctttggtgctggtcctgttggtcttttggctgctgctgtcgccaagaccttcggtgctaagggtgtcatcgtcgttgacattttcgacaacaagttgaagatggccaaggacattggtgctgctactcacaccttcaactccaagaccggtggttctgaagaattgatcaaggctttcggtggtaacgtgccaaacgtcgttttggaatgtactggtgctgaaccttgtatcaagttgggtgttgacgccattgccccaggtggtcgtttcgttcaagttggtaacgctgctggtccagtcagcttcccaatcaccgttttcgccatgaaggaattgactttgttcggttctttcagatacggattcaacgactacaagactgctgttggaatctttgacactaactaccaaaacggtagagaaaatgctccaattgactttgaacaattgatcacccacagatacaagttcaaggacgctattgaagcctacgacttggtcagagccggtaagggtgctgtcaagtgtctcattgacggccctgagtaa")


    ampl = cloning_primers(xdh, maxlength=29, fp_tail ="aa", rp_tail = "", formula = tmbresluc)

    #ampl = cloning_primers(sgd.promoter("FBA1"), maxlength=29, fp_tail =ftail, rp_tail = rtail, formula = "tmbresluc")

    print ampl.detailed_figure()

    #ampl = cloning_primers(sgd.promoter("TEF1"),29, fp = primer[417], rp_tail = tail)

#    print ampl.forward_primer.primer.seq
#    print ampl.reverse_primer.primer.seq

    #print rp.seq
    #fp, rp = cloning_primers(sgd.promoter("TPI1"),29,fp = primer[419], rp_tail = tail)
    #print rp.seq
    #fp, rp = cloning_primers(sgd.promoter("PDC1"),29,fp = primer[413], rp_tail = tail)
    #print rp.seq
    #fp, rp = cloning_primers(sgd.promoter("FBA1"),29,fp = primer[409], rp_tail = tail)
    #print rp.seq
    #fp, rp = cloning_primers(sgd.promoter("TDH3"),29,fp = primer[415], rp_tail = tail)
    #print rp.seq




