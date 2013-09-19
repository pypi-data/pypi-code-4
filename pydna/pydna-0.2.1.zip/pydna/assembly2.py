#!/usr/bin/env python
# -*- coding: utf-8 -*-


import copy
import itertools
import networkx as nx
import operator
import random
from collections import defaultdict
from collections import namedtuple

from Bio.SeqFeature import ExactPosition
from Bio.SeqFeature import FeatureLocation
from Bio.SeqFeature import SeqFeature

from pydna import Dseq
from pydna import Dseqrecord
from pydna._simple_paths7 import all_circular_paths_edges
from pydna._simple_paths8 import all_simple_paths_edges
from findsubstrings_suffix_arrays_python import common_sub_strings
from findterminaloverlap_indexof_python import terminal_overlap

def _add_tr_features(dsrecs, limit):
    #dsrecs=list(copy.deepcopy(dsrecs))
    cols = {}
    for dsrec in dsrecs:
        dsrec.features = [f for f in dsrec.features if f.type!="overlap"]
        dsrec.seq = dsrec.seq.fill_in()
    rcs = {dsrec:dsrec.rc() for dsrec in dsrecs}
    matches=[]
    dsset=set()

    for a, b in itertools.permutations(dsrecs, 2):
        match = terminal_overlap(str(a.seq).lower(), 
                                 str(b.seq).lower(), 
                                 limit)
        if match:
            matches.append((a, b, match))
            dsset.add(a)
            dsset.add(b)

        match = common_sub_strings(str(a.seq).lower(),
                                   str(rcs[b].seq).lower(),
                                                limit)
        if match:
            matches.append((a, rcs[b], match))
            dsset.add(a)
            dsset.add(rcs[b])

    for a,b,match in matches: 
        for start_in_a, start_in_b, length in match:
    
            chksum = a[start_in_a:start_in_a+length].seguid()
            assert chksum == b[start_in_b:start_in_b+length].seguid()
            
            try:
                fcol, revcol = cols[chksum]
            except KeyError:
                fcol = '#%02X%02X%02X' % (random.randint(175,255),random.randint(175,255),random.randint(175,255))
                rcol = '#%02X%02X%02X' % (random.randint(175,255),random.randint(175,255),random.randint(175,255))
                cols[chksum] = fcol,rcol
            
            qual      = {"note"             : ["olp_{}".format(chksum)],
                         "chksum"           : [chksum],
                         "ApEinfo_fwdcolor" : [fcol],
                         "ApEinfo_revcolor" : [rcol]}
            
            if not chksum in [f.qualifiers["chksum"][0] for f in a.features if f.type == "overlap"]:            
                a.features.append( SeqFeature( FeatureLocation(start_in_a,
                                                               start_in_a + length),
                                                               type = "overlap",
                                                               qualifiers = qual))
            if not chksum in [f.qualifiers["chksum"][0] for f in b.features if f.type == "overlap"]:
                b.features.append( SeqFeature( FeatureLocation(start_in_b,
                                                               start_in_b + length),
                                                               type = "overlap",
                                                               qualifiers = qual))
    for ds in dsset:
        ds.features = sorted([f for f in ds.features], key = operator.attrgetter("location.start")) 
    return list(dsset)
    
    

def _add_hr_features(dsrecs, limit):    
    #dsrecs=list(copy.deepcopy(dsrecs))
    cols = {}
    for dsrec in dsrecs:
        dsrec.features = [f for f in dsrec.features if f.type!="overlap"]
        dsrec.seq = dsrec.seq.fill_in()
    #rcs = [dsrec.rc() for dsrec in dsrecs]
    rcs = {dsrec:dsrec.rc() for dsrec in dsrecs}
    matches=[]
    dsset=set()

    for a, b in itertools.combinations(dsrecs, 2):
        match = common_sub_strings(str(a.seq).upper(),
                                   str(b.seq).upper(),
                                                limit)
        if match:
            matches.append((a, b, match))
            dsset.add(a)
            dsset.add(b)
            
        match = common_sub_strings(str(a.seq).upper(),
                                   str(rcs[b].seq).upper(),
                                                limit)
        if match:
            matches.append((a, rcs[b], match))
            dsset.add(a)
            dsset.add(rcs[b])

#    for a in set(dsrecs) - dsset:
#        for rc in rcs:
#            match = common_sub_strings(str(a.seq).upper(),
#                                       str(rc.seq).upper(),
#                                       limit)
#            if match:
#                matches.append((a, rc, match))
#                #matches.append((a.rc(), b, [(len(a)-sa-le, len(b)-sb-le, le) for sa,sb,le in match]))

    for a,b,match in matches: 
        for start_in_a, start_in_b, length in match:
#            dsset.add(a)
#            dsset.add(b)
            chksum = a[start_in_a:start_in_a+length].seguid()
            assert chksum == b[start_in_b:start_in_b+length].seguid()
            
            try:
                fcol, revcol = cols[chksum]
            except KeyError:
                fcol = '#%02X%02X%02X' % (random.randint(175,255),random.randint(175,255),random.randint(175,255))
                rcol = '#%02X%02X%02X' % (random.randint(175,255),random.randint(175,255),random.randint(175,255))
                cols[chksum] = fcol,rcol
            
            qual      = {"note"             : ["olp_{}".format(chksum)],
                         "chksum"           : [chksum],
                         "ApEinfo_fwdcolor" : [fcol],
                         "ApEinfo_revcolor" : [rcol]}
            
            if not chksum in [f.qualifiers["chksum"][0] for f in a.features if f.type == "overlap"]:            
                a.features.append( SeqFeature( FeatureLocation(start_in_a,
                                                               start_in_a + length),
                                                               type = "overlap",
                                                               qualifiers = qual))
            if not chksum in [f.qualifiers["chksum"][0] for f in b.features if f.type == "overlap"]:
                b.features.append( SeqFeature( FeatureLocation(start_in_b,
                                                               start_in_b + length),
                                                               type = "overlap",
                                                               qualifiers = qual))
    for ds in dsset:
        ds.features = sorted([f for f in ds.features], key = operator.attrgetter("location.start"))          

    return list(dsset)
    
    
    
    
    
    
    
    

def _create_graph(dsrecs):
    
    G=nx.MultiDiGraph( multiedges=True, selfloops=False)
    G.add_node( '5' ) #, sek=Dseqrecord(''))
    G.add_node( '3' ) #, sek=Dseqrecord(''))
    
    for dsrec in dsrecs:
        overlaps = sorted( {f.qualifiers['chksum'][0]:f for f in dsrec.features 
                            if f.type=='overlap'}.values(),
                           key = operator.attrgetter('location.start'))          

        if overlaps:
            overlaps = ([SeqFeature(FeatureLocation(0,0),
                         type = 'overlap',
                         qualifiers = {'chksum':['5']})]+
                         overlaps+
                        [SeqFeature(FeatureLocation(len(dsrec),len(dsrec)),
                                    type = 'overlap',
                                    qualifiers = {'chksum':['3']})])
            
            for olp1, olp2 in itertools.combinations(overlaps, 2):
                
                n1 = olp1.qualifiers['chksum'][0]
                n2 = olp2.qualifiers['chksum'][0]
                
                if n1 == '5' and n2=='3':
                    continue   
                
                s1,e1,s2,e2 = (olp1.location.start.position,
                               olp1.location.end.position,
                               olp2.location.start.position,
                               olp2.location.end.position,)
                
                #start, end = olp1.location.end, olp2.location.start
                
                #sek = dsrec[start:end]
                #sek = dsrec[e1:s2]
                
                #begin, stop = int(olp1.location.start), int(olp2.location.end)
                
                #processed_sek = dsrec[begin:stop]
                processed_sek = dsrec[s1:e2]
                    
#                processed_sek = Dseqrecord(Dseq(
#                                watson = processed_sek.seq.watson[:len(processed_sek.seq.watson)-len(olp2)],
#                                crick  = processed_sek.seq.crick[:len(processed_sek.seq.crick)-len(olp1)],
#                                ovhg   = -len(olp1)))
            
                processed_sek = Dseqrecord(Dseq(
                                watson = processed_sek.seq.watson[e1-s1:],
                                crick  = processed_sek.seq.crick[e2-s2:],
                                ovhg   = e1-s1))
                
                
                #if start>end:
#                if e1>s2:
#                    sek=Dseqrecord((e1-s2)*'-') # tandem overlaps overlap with each other !
                        
                G.add_edge(n1, n2, #sek=sek, 
                                   dsrec=dsrec, 
                                   processed_sek = processed_sek, 
                                   start1=s1,
                                   end1=e1,
                                   start2=s2,
                                   end2=e2)
#                G.node[n1]['sek'] = olp1.extract(dsrec)
#                G.node[n2]['sek'] = olp2.extract(dsrec)        
    return G


def _recombination_assembly(dsrecs, homology_alg, limit):
    
    assembly = namedtuple('assembly', 'result source_fragments sticky_fragments source_alignments sticky_alignments overlap_sizes')
    
    dsrecs = homology_alg(dsrecs, limit)
    
    max_nodes = len(dsrecs)

#    for d in dsrecs:
#        import time
#        ape(d)
#        time.sleep(0.5)
#    import sys;sys.exit()
    
    lG = _create_graph(dsrecs)    
    cG = lG.copy()    
    cG.remove_nodes_from(('5','3'))
    circular_products=defaultdict(list)
    
#    all_circular_paths_edges_=[]                                        #
#    for path in all_circular_paths_edges(cG):                           #
#        all_circular_paths_edges_.append(path)                          #
#    all_circular_paths_edges_=[all_circular_paths_edges_[1],]           #

    for path in all_circular_paths_edges(cG):     

        first_node, second_node, edgedict = path[0]
        sticky_alignments = [0, edgedict['start2']-edgedict['start1']]
        source_alignments = [0, edgedict['start2'], ]
        source_seqs=[edgedict['dsrec'],]
        sticky_source_seqs=[edgedict['processed_sek'],]
        #esek=edgedict['sek']
        overlap_sizes = [0, edgedict['end2']-edgedict['start2']]
        
        #if esek.seq.watson == len(esek.seq.watson)*'-':
        if edgedict['start2']<edgedict['end1']:
            #result=cG.node[second_node]['sek'][len(esek):]
            #result=edgedict['dsrec'][edgedict['start1']:edgedict['start1']+len(esek)]
            result=edgedict['dsrec'][edgedict['start2']+(edgedict['end1']-edgedict['start2']):edgedict['end2']]
        else:
            #result=esek+cG.node[second_node]['sek']
            result=edgedict['dsrec'][edgedict['end1']:edgedict['end2']]
        
        for first_node, second_node, edgedict in path[1:]:            
            #esek=edgedict['sek']
            source_seqs.append(edgedict['dsrec'])
            sticky_source_seqs.append(edgedict['processed_sek'])
            overlap_sizes.append(edgedict['end2']-edgedict['start2'])
            #if esek.seq.watson == len(esek.seq.watson)*'-':
            if edgedict['start2']<edgedict['end1']:
                #result+=cG.node[second_node]['sek'][len(esek):]
                #print cG.node[second_node]['sek'][len(esek):]
                result+=edgedict['dsrec'][edgedict['start2']+(edgedict['end1']-edgedict['start2']):edgedict['end2']]                
                #raw_input("zzz")
            else:
                #result+=e
                #result+=cG.node[second_node]['sek']
                result+=edgedict['dsrec'][edgedict['end1']:edgedict['end2']]

            #sticky_alignments.append( len(result) )
            #source_alignments.append( sticky_alignments[-2] - edgedict['start1'] + hej )
            
            sticky_alignments.append( sticky_alignments[-1] + edgedict['start2'] - edgedict['start1'] )
            source_alignments[-1] -= edgedict['start1']
            source_alignments.append( source_alignments[-1] + edgedict['start2'] )
            
        add=True
        for cp in circular_products[len(result)]:
            if (str(result.seq).lower() in str(cp.result.seq).lower()*2
                or
                str(result.seq).lower() == str(cp.result.seq.reverse_complement()).lower()*2):
                add=False                
        if add:
            circular_products[len(result)].append( assembly(Dseqrecord(result, circular = True), source_seqs, sticky_source_seqs, source_alignments[:-1], sticky_alignments[:-1], overlap_sizes) )

    circular_products = list(itertools.chain.from_iterable(circular_products[size] for size in sorted(circular_products, reverse=True)))
    
    linear_products=defaultdict(list)    
    pw = []
    sticky_source_seqs=[]
    
#    for d in dsrecs:
#        import time
#        ape(d)
#        time.sleep(0.5)
#    import sys;sys.exit()

    
    for path in all_simple_paths_edges(lG, '5', '3', data=True, cutoff=max_nodes):
#        sticky_alignments = [0]
#        source_alignments = []
#        source_seqs=[]
#        sticky_source_seqs=[]
#        result = Dseqrecord('')
        
        
        first_node, second_node, edgedict = path[0]
        edgedict = edgedict.values().pop()
        #print first_node, second_node, edgedict
        sticky_alignments = [0, edgedict['start2']-edgedict['start1']]
        source_alignments = [0, edgedict['start2'], ]
        source_seqs=[edgedict['dsrec'],]
        sticky_source_seqs=[edgedict['processed_sek'],]
        #esek=edgedict['sek']
        overlap_sizes = [0, edgedict['end2']-edgedict['start2']]
        
        #if esek.seq.watson == len(esek.seq.watson)*'-':
        if edgedict['start2']<edgedict['end1']:
            #result=cG.node[second_node]['sek'][len(esek):]
            result=edgedict['dsrec'][edgedict['start2']+(edgedict['end1']-edgedict['start2']):edgedict['end2']]
        else:
            #result=esek+cG.node[second_node]['sek']
            result=edgedict['dsrec'][edgedict['end1']:edgedict['end2']]
            
        for first_node, second_node, ed in path[1:]:
            
            edgedict=ed.values().pop()
            #e=edgedict['sek']
            source_seqs.append(edgedict['dsrec'])
            sticky_source_seqs.append(edgedict['processed_sek'])
            
            #if e.seq.watson == len(e.seq.watson)*'-':
            if edgedict['start2']<edgedict['end1']:
                #result+=lG.node[second_node]['sek'][len(e):]
                result+=edgedict['dsrec'][edgedict['start2']+(edgedict['end1']-edgedict['start2']):edgedict['end2']] 
            else:
                #result+=e
                #result+=lG.node[second_node]['sek']
                result+=edgedict['dsrec'][edgedict['end1']:edgedict['end2']]
                
#            sticky_alignments.append( len(result) - len(lG.node[second_node]['sek']))
#            source_alignments.append( sticky_alignments[-2] - h['start1'])
            sticky_alignments.append( sticky_alignments[-1] + edgedict['start2'] - edgedict['start1'] )
            source_alignments[-1] -= edgedict['start1']
            source_alignments.append( source_alignments[-1] + edgedict['start2'] )
            overlap_sizes.append(edgedict['end2']-edgedict['start2'])
            

        add=True
        for lp in linear_products[len(result)]:
            if (str(result.seq).lower() == str(lp.result.seq).lower()
                or
                str(result.seq).lower() == str(lp.result.seq.reverse_complement()).lower()):
                add=False
        for dsrec in dsrecs:
            if (str(result.seq).lower() == str(dsrec.seq).lower()
                or
                str(result.seq).lower() == str(dsrec.seq.reverse_complement()).lower()):
                add=False
        if add:
            linear_products[len(result)].append(assembly( Dseqrecord(result, linear = True), source_seqs, sticky_source_seqs, source_alignments[:-1], sticky_alignments[:-1], overlap_sizes[:-1]) )

    linear_products = list(itertools.chain.from_iterable(linear_products[size] for size in sorted(linear_products, reverse=True)))
    
    products = namedtuple('products', 'linear circular')
    
    return products(linear_products, circular_products)
    
def gibson_assembly(dsrecs, limit=15):
    '''Accepts a list of Dseqrecords and tries to assemble them into
    linear or circular assemblies based on shared regions of homology at the 
    extremities of each fragment with a minimum length given by limit.
    
    This is a simulation of the DNA assembly method described in:
    
    Gibson DG, Young L, Chuang R-Y, Venter JC, Hutchison CA 3rd, Smith HO (2009)
    Enzymatic assembly of DNA molecules up to several hundred kilobases. 
    Nat Methods 6:343–345. doi: 10.1038/nmeth.1318

    Parameters
    ----------
    dsrecs : list
        a list of Dseqrecord objects.

    limit : int, optional
        limit is set to 15 nucleotides by default.

    Returns
    -------
    linear, circular : tuple
        Linear and circular are two lists containing linear 
        and circular assemblies.

        Each object in linear or circular is a named tuple with the following
        fields:
        
        +------------------+---------------------+----------------------------+ 
        | Field            | Type                | Contains                   | 
        +==================+=====================+============================+ 
        | result           | Dseqrecord          | Assembeled sequence        |
        +------------------+---------------------+----------------------------+ 
        | fragments        | list of Dseqrecords | list of fragments          | 
        +------------------+---------------------+----------------------------+ 
        | alignments       | list of integers    | list of cumulative alignments |
        |                  |                     | aligning each source       |
        |                  |                     | fragment                   |
        +------------------+------------+--------+----------------------------+      
        | overlap_sizes    | list of integers    | list of the length of each |
        |                  |                     | overlap joining the        |   
        |                  |                     | sequences                  |
        +------------------+---------------------+----------------------------+ 
        
        Source fragments are the double stranded blunt DNA fragments 
        originally added as the dsrecs argument. The parwise overlaps 
        found are added ar features to the source fragments.
        
        alignments is a list with the cumulative stagger between 
        each fragment.

        ::        
        
                        <--6->        <--6->        overlap_sizes = [6,6]
                        
            cggcggcgggccTGCCTC                      \\
            gccgccgcccgg                             | 
                                                     |
                              accattgcAAAAAA         | sticky_fragments = [12,26]
                        ACGGAGtggtaacg               |
                                                     | 
                                            catcata  | 
                                      TTTTTTgtagtat  /
                                            
            <---------->
            <------------------------>              alignments
    '''
    
    
    
    
    pl, pc = _recombination_assembly(dsrecs, _add_tr_features, limit)

    products = namedtuple('products', 'linear circular')
    assembly = namedtuple('assembly', 'result fragments alignments overlap_sizes')

    linear_results=[]
    circular_results=[]

    for a in pl:
        linear_results.append( assembly(result        = a.result,
                                        fragments     = a.sticky_fragments,
                                        alignments       = a.sticky_alignments,
                                        overlap_sizes = a.overlap_sizes))
    for a in pc:
        circular_results.append( assembly(result        = a.result,
                                          fragments     = a.sticky_fragments,
                                          alignments       = a.sticky_alignments,
                                          overlap_sizes = a.overlap_sizes))
        
    return products(linear=linear_results, circular=circular_results)

def recombination_assembly(dsrecs, limit=25):
    '''Accepts a list of Dseqrecords and tries to assemble them into
    linear and circular assemblies based on shared regions of homology 
    with a minimum length given by limit.

    Parameters
    ----------

    dsrecs : list
        a list of Dseqrecord objects.

    limit : int, optional
        limit is set to 25 nucleotides by default.

    Returns
    -------
    linear, circular: tuple
        Linear and circular are two lists containing linear 
        and circular assemblies.

        Each object in linear or circular is a named tuple with the following
        fields        

        +------------------+---------------------+----------------------------+ 
        | Field            | Type                | Contains                   | 
        +==================+=====================+============================+ 
        | result           | Dseqrecord          | Assembeled sequence        |
        +------------------+---------------------+----------------------------+ 
        | source_fragments | list of Dseqrecords | list of fragments          | 
        +------------------+---------------------+----------------------------+ 
        | sticky_fragments | list of Dseqrecords | list of processed fragments|
        |                  |                     | with a single stranded 5'  | 
        |                  |                     | cohesive end               |
        +------------------+---------------------+----------------------------+
        | source_alignments   | list of integers    | list of cumulative alignments |
        |                  |                     | aligning each source       |
        |                  |                     | fragment                   |
        +------------------+------------+--------+----------------------------+
        | sticky_alignments   | list of integers    | list of cumulative alignments |
        |                  |                     | aligning each sticky       |
        |                  |                     | fragment                   |
        +------------------+------------+--------+----------------------------+       
        | overlap_sizes    | list of integers    | list of the length of each |
        |                  |                     | overlap joining the        |   
        |                  |                     | sequences                  |
        +------------------+---------------------+----------------------------+        


        Source fragments are the double stranded blunt DNA fragments 
        originally added as the dsrecs argument. The parwise overlaps 
        found are added ar features to the source fragments.
        
        Sticky fragments are source fragments that have been processed 
        so that they can be ligated together by the homologous repair DNA
        machinery (single-strand annealing pathway). This involves trimming 
        DNA fragments so that the fragments are flanked by a 5' single stranded
        overhang.   
        
        Source_alignments is a list with the cumulative stagger between 
        each source fragment. Source alignments are different from sticky 
        alignments when the overlapping sequences are located in the interior
        of the fragments.

        ::
            
            Source fragments         
            ----------------
            
            
            cggcggcgggccTGCCTCtc                    \\
            gccgccgcccggACGGAGag                    | 
                                                    |
                      taTGCCTCaccattgcAAAAAAtt      |  source_fragments
            <-------->atACGGAGtggtaacgTTTTTTaa      |
                                                    | 
                                   aatAAAAAAcatcata | 
            <--------------------->ttaTTTTTTgtagtat /
            
            source_alignments = [10,23]
            
            
            Processed fragments         
            -------------------
            
                        <--6->        <--6->        overlap_sizes = [6,6]
                     
            cggcggcgggccTGCCTC                      \\
            gccgccgcccgg                             | 
                                                     |
                              accattgcAAAAAA         | sticky_fragments = [12,26]
            <---------->ACGGAGtggtaacg               |
                                                     | 
                                            catcata  | 
            <------------------------>TTTTTTgtagtat  /
                   sticky_alignments
                           
        

    '''
    return _recombination_assembly(dsrecs, _add_hr_features, limit)

def fusion_pcr_assembly(dsrecs, limit=15):
    '''Accepts a list of Dseqrecords and tries to assemble them into
    linear assemblies based on shared regions of homology at the 
    extremities of each fragment with a minimum length given by limit.

    Parameters
    ----------

    dsrecs : list
        a list of Dseqrecord objects.

    limit : int, optional
        limit is set to 15 nucleotides by default.

    Returns
    -------
    linear: list
        Each object in linear is a named tuple with the following
        fields:
        
        +------------------+---------------------+----------------------------+ 
        | Field            | Type                | Contains                   | 
        +==================+=====================+============================+ 
        | result           | Dseqrecord          | Assembeled sequence        |
        +------------------+---------------------+----------------------------+ 
        | fragments        | list of Dseqrecords | list of fragments          | 
        +------------------+---------------------+----------------------------+ 
        | alignments          | list of integers    | list of cumulative alignments |
        |                  |                     | aligning each source       |
        |                  |                     | fragment                   |
        +------------------+------------+--------+----------------------------+      
        | overlap_sizes    | list of integers    | list of the length of each |
        |                  |                     | overlap joining the        |   
        |                  |                     | sequences                  |
        +------------------+---------------------+----------------------------+ 
        
        Source fragments are the double stranded blunt DNA fragments 
        originally added as the dsrecs argument. The parwise overlaps 
        found are added ar features to the source fragments.
        
        alignments is a list with the cumulative stagger between 
        each fragment.

        ::
            
                        <--6->        <--6->         overlap_sizes = [6,6]
                                    
            cggcggcgggccTGCCTC                      \\
            gccgccgcccggACGGAG                      | 
                                                    |
                        TGCCTCaccattgcAAAAAA        | fragments
                        ACGGAGtggtaacgTTTTTT        |
                                                    | 
                                      AAAAAAcatcata | 
                                      TTTTTTgtagtat /

            <---------->
            <----------------------->               alignments = [12,26]
                        
    '''


    p = _recombination_assembly(dsrecs, _add_tr_features, limit).linear
    if not p:
        return []
    assembly = namedtuple('assembly', 'result fragments alignments overlap_sizes')
    results=[]    
    for a in p:
        results.append( assembly(result = a.result,
                                 fragments = a.source_fragments,
                                 alignments = a.source_alignments,
                                 overlap_sizes =  a.overlap_sizes))            
    return results

if __name__=="__main__":
    from pydna_helper import ape
    from pydna import Dseqrecord, parse, eq
    
    a=Dseqrecord( "atgatcagagTATCTATctTGCCTCATATAAA")                                
    b=Dseqrecord(                    "TGCCTCATATAAAaccaagcatctattagacgtgtatcta")
    prods = fusion_pcr_assembly( (a,b), 13)
    
    for seq, spc, olp in zip(prods[0].fragments, 
                             prods[0].alignments,
                             prods[0].overlap_sizes):
        print " "*spc+"|"*olp
        print " "*spc+str(seq.seq)

#    for d in (a,b):
#        import time
#        ape(d)
#        time.sleep(0.5)
#    import sys;sys.exit()

    a=Dseqrecord( "atgatcagagTATCTATctTGCCTCATATAAA")                                
    b=Dseqrecord(                    "tagatacacgtctaatagatgcttggtTTTATATGAGGCA")
    prods = fusion_pcr_assembly( (a,b), 13)
       
    for seq, spc, olp in zip(prods[0].fragments, 
                             prods[0].alignments,
                             prods[0].overlap_sizes):
        print " "*spc+"|"*olp
        print " "*spc+str(seq.seq)


    a=Dseqrecord( "cggcggcgggccTGCCTC")                                  
    b=Dseqrecord(             "TGCCTCaccattgcAAAAAA")
    c=Dseqrecord(                           "AAAAAAcatcata" )
                                                                      
    prods = gibson_assembly( (a,b,c), 6).linear
    
    for seq, spc, olp in zip(prods[0].fragments, 
                             prods[0].alignments,
                             prods[0].overlap_sizes):
        print " "*spc+"|"*olp
        print " "*spc+str(seq.seq)
    
    print prods[0].fragments[2]


    a=Dseqrecord( "atgatcagagTATCTATctTGCCTCATATAAAc")                                
    b=Dseqrecord(                   "gTGCCTCATATAAAaccaagcatctattagacgtgtatcta")
    prods = recombination_assembly( (a,b), 13)
    
    
    
    
    for seq, spc, olp in zip(prods.linear[0].sticky_fragments, 
                             prods.linear[0].sticky_alignments,
                             prods.linear[0].overlap_sizes):
        print " "*spc+"|"*olp
        print " "*spc+str(seq.seq)
        
    for seq, spc, spc2, olp in zip(prods.linear[0].source_fragments, 
                                   prods.linear[0].source_alignments,
                                   prods.linear[0].sticky_alignments,                 
                                   prods.linear[0].overlap_sizes):
        print " "*spc2+"|"*olp
        print " "*spc+str(seq.seq)

    a=Dseqrecord( "atgatcagagTATCTATctTGCCTCATATAAAc")                                
    b=Dseqrecord( "tagatacacgtctaatagatgcttggtTTTATATGAGGCAc")
    prods = recombination_assembly( (a,b), 13)
    
    for seq, spc, olp in zip(prods.linear[0].sticky_fragments, 
                             prods.linear[0].sticky_alignments,
                             prods.linear[0].overlap_sizes):
        print " "*spc+"|"*olp
        print " "*spc+str(seq.seq)
        
    for seq, spc, spc2, olp in zip(prods.linear[0].source_fragments, 
                                   prods.linear[0].source_alignments,
                                   prods.linear[0].sticky_alignments,                 
                                   prods.linear[0].overlap_sizes):
        print " "*spc2+"|"*olp
        print " "*spc+str(seq.seq)
    
    print prods.__class__
    print prods.linear[0].overlap_sizes
        
    a=Dseqrecord( "cggcggcgggccTGCCTCtc")                                  
    b=Dseqrecord(            "aTGCCTCaccattgcAAAAAAtt")
    c=Dseqrecord(                          "tAAAAAAcatcata" )
                                                                      
    prods = recombination_assembly( (a,b,c), 6)
    for seq, spc in zip(prods.linear[0].sticky_fragments, prods.linear[0].sticky_alignments):
        print " "*spc+str(seq.seq)
    for seq, spc in zip(prods.linear[0].source_fragments, prods.linear[0].source_alignments):
        print " "*spc+str(seq.seq)
    
    assert prods.linear[0].result.seq.tostring() == "cggcggcgggccTGCCTCaccattgcAAAAAAcatcata"
    
    print prods.linear[0].overlap_sizes
    
    a=Dseqrecord(                              "TATATCATATAAAnnGGGCGCGGGCGGC")                                  
    b=Dseqrecord(              "GGGCGCGGGCGGCNNNTATATCATATAAA")

    prods = gibson_assembly( (a ,b), 13)

    assert eq( prods.circular[0].result, Dseqrecord("TATATCATATAAAnnGGGCGCGGGCGGCNNN", circular=True) )


    for seq, spc in zip(prods.circular[0].fragments, prods.circular[0].alignments):
        print " "*spc+str(seq.seq)
        
    print prods.circular[0].overlap_sizes
    
    a=Dseqrecord(                    "aaTATATCATATAAAnnGGGCGCGGGCGGCtt")                                  
    b=Dseqrecord(                    "ccGGGCGCGGGCGGCNNNTATATCATATAAAaa")

    prods = recombination_assembly( (a,b), 13)
    
    assert eq( prods.circular[0].result, Dseqrecord("TATATCATATAAAnnGGGCGCGGGCGGCNNN", circular=True) )

    for seq, spc in zip(prods.circular[0].sticky_fragments, prods.circular[0].sticky_alignments):
        print " "*spc+str(seq.seq)
    for seq, spc in zip(prods.circular[0].source_fragments, prods.circular[0].source_alignments):
        print " "*spc+str(seq.seq)
        
    a=Dseqrecord( "nGGGGGGatgatcagagTATCTATctTGCCTCtc")                                  
    b=Dseqrecord(                          "aTGCCTCaccatgcactTATCTATtgcAAAAAAtt")
    c=Dseqrecord(                                                    "tAAAAAAnncGGGGGGt" )
                                                                      
    prods = recombination_assembly( (a,b,c), 6)
    
    assert prods.circular[0].result.seq.tostring().lower() == "accatgcactTATCTATtgcAAAAAAnncGGGGGGatgatcagagTATCTATctTGCCTC".lower()
    
    for seq, spc in zip(prods.circular[0].sticky_fragments, prods.circular[0].sticky_alignments):
        print " "*spc+str(seq.seq)
    for seq, spc in zip(prods.circular[0].source_fragments, prods.circular[0].source_alignments):
        print " "*spc+str(seq.seq)
        
    print prods.circular[0].overlap_sizes
        

    text5 = '''

    >2577
    tcctgacgggtaattttgatttgcatgccgtccgggtgagtcatagcgtctggttgttttgccagattcagcagagtctgtgcaatgcggccgctgacagagtcttttgtaacgaccccgtctccaccaacttggtatgcttgaaatctcaaggccattacacattcagttatgtgaacgaaaggtctttatttaacgtagcataaactaaataatacaggttccggttagcctgcaatgtgttaaatctaaaggagcatacccaaaatgaactgaagacaaggaaatttgcttgtccagatgtgattgagcatttgaacgttaataacataacatttttatacttaactatagaaagacttgtataaaaactggcaaacgagatattctgaatattggtgcatatttcaggtagaaaagcttacaaaacaatctaatcataatattgagatgaagagaaagataaaagaaaaaacgataagtcagatgagattatgattgtactttgaaatcgaggaacaaagtatatacggtagtagttccccgagttataacgggagatcatgtaaattgagaaaccagataaagatttggtatgcactctagcaagaaaataaaatgatgaatctatgatatagatcacttttgttccagcgtcgaggaacgccaggttgcccactttctcactagtgacctgcagccgacgatcagatctttcaggaaagtttcggaggagatagtgttcggcagtttgtacatcatctgcgggatcaggtacggtttgatcaggttgtagaagatcaggtaagacatagaatcgatgtagatgatcggtttgtttttgttgatttttacgtaacagttcagttggaatttgttacgcagacccttaaccaggtattctacttcttcgaaagtgaaagactgggtgttcagtacgatcgatttgttggtagagtttttgttgtaatcccatttaccaccatcatccatgaaccagtatgccagagacatcggggtcaggtagttttcaaccaggttgttcgggatggtttttttgttgttaacgatgaacaggttagccagtttgttgaaagcttggtgtttgaaagtctgggcgccccaggtgattaccaggttacccaggtggttaacacgttcttttttgtgcggcggggacagtacccactgatcgtacagcagacatacgtggtccatgtatgctttgtttttccactcgaactgcatacagtaggttttaccttcatcacgagaacggatgtaagcatcacccaggatcagaccgatacctgcttcgaactgttcgatgttcagttcgatcagctgggatttgtattctttcagcagtttagagttcggacccaggttcattacctggttttttttgatgtttttcatatgcatggatccggggttttttctccttgacgttaaagtatagaggtatattaacaattttttgttgatacttttattacatttgaataagaagtaatacaaaccgaaaatgttgaaagtattagttaaagtggttatgcagtttttgcatttatatatctgttaatagatcaaaaatcatcgcttcgctgattaattaccccagaaataaggctaaaaaactaatcgcattatcatcctatggttgttaatttgattcgttcatttgaaggtttgtggggccaggttactgccaatttttcctcttcataaccataaaagctagtattgtagaatctttattgttcggagcagtgcggcgcgaggcacatctgcgtttcaggaacgcgaccggtgaagacgaggacgcacggaggagagtcttccttcggagggctgtcacccgctcggcggcttctaatccgtacttcaatatagcaatgagcagttaagcgtattactgaaagttccaaagagaaggtttttttaggctaagataatggggctctttacatttccacaacatataagtaagattagatatggatatgtatatggatatgtatatggtggtaatgccatgtaatatgattattaaacttctttgcgtccatccaacgagatctggcgcgccttaattaacccaacctgcattaatgaatcggccaacgcgcggattaccctgttatccctacatattgttgtgccatctgtgcagacaaacgcatcaggattcagtactgacaataaaaagattcttgttttcaagaacttgtcatttgtatagtttttttatattgtagttgttctattttaatcaaatgttagcgtgatttatattttttttcgcctcgacatcatctgcccagatgcgaagttaagtgcgcagaaagtaatatcatgcgtcaatcgtatgtgaatgctggtcgctatactgctgtcgattcgatactaacgccgccatccagtgtcgaaaacgagctcgaattcatcgatgatatcagatccactagtggcctatgcggccgcggatctgccggtctccctatagtgagtcgatccggatttacctgaatcaattggcgaaattttttgtacgaaatttcagccacttcacag

    >2389
    tcctgacgggtaattttgatttgcatgccgtccgggtgagtcatagcgtctggttgttttgccagattcagcagagtctgtgcaatgcggccgctgaccacatacgatttaggtgacactatagaacgcggccgccagctgaagcttcgtacgctgcaggtcgacggatccccgggttaattaaggcgcgccagatctgtttagcttgccttgtccccgccgggtcacccggccagcgacatggaggcccagaataccctccttgacagtcttgacgtgcgcagctcaggggcatgatgtgactgtcgcccgtacatttagcccatacatccccatgtataatcatttgcatccatacattttgatggccgcacggcgcgaagcaaaaattacggctcctcgctgcagacctgcgagcagggaaacgctcccctcacagacgcgttgaattgtccccacgccgcgcccctgtagagaaatataaaaggttaggatttgccactgaggttcttctttcatatacttccttttaaaatcttgctaggatacagttctcacatcacatccgaacataaacaaccgtcgaggaacgccaggttgcccactttctcactagtgacctgcagccgacccaatcacatcacatccgaacataaacaaccatgggtaaaaagcctgaactcaccgcgacgtctgtcgagaagtttctgatcgaaaagttcgacagcgtctccgacctgatgcagctctcggagggcgaagaatctcgtgctttcagcttcgatgtaggagggcgtggatatgtcctgcgggtaaatagctgcgccgatggtttctacaaagatcgttatgtttatcggcactttgcatcggccgcgctcccgattccggaagtgcttgacattggggaattcagcgagagcctgacctattgcatctcccgccgtgcacagggtgtcacgttgcaagacctgcctgaaaccgaactgcccgctgttctgcagccggtcgcggaggccatggatgcgatcgctgcggccgatcttagccagacgagcgggttcggcccattcggaccgcaaggaatcggtcaatacactacatggcgtgatttcatatgcgcgattgctgatccccatgtgtatcactggcaaactgtgatggacgacaccgtcagtgcgtccgtcgcgcaggctctcgatgagctgatgctttgggccgaggactgccccgaagtccggcacctcgtgcacgcggatttcggctccaacaatgtcctgacggacaatggccgcataacagcggtcattgactggagcgaggcgatgttcggggattcccaatacgaggtcgccaacatcttcttctggaggccgtggttggcttgtatggagcagcagacgcgctacttcgagcggaggcatccggagcttgcaggatcgccgcggctccgggcgtatatgctccgcattggtcttgaccaactctatcagagcttggttgacggcaatttcgatgatgcagcttgggcgcagggtcgatgcgacgcaatcgtccgatccggagccgggactgtcgggcgtacacaaatcgcccgcagaagcgcggccgtctggaccgatggctgtgtagaagtactcgccgatagtggaaaccgacgccccagcactcgtccgagggcaaaggaataatcagtactgacaataaaaagattcttgtagggataacagggtaatcggagtgccatctgtgcagacaaacgcatcaggatagagtcttttgtaacgaccccgtctccaccaacttggtatgcttgaaatctcaaggccattacacattcagttatgtgaacgaaaggtctttatttaacgtagcataaactaaataatacaggttccggttagcctgcaatgtgttaaatctaaaggagcatacccaaaatgaactgaagacaaggaaatttgcttgtccagatgtgattgagcatttgaacgttaataacataacatttttatacttaactatagaaagacttgtataaaaactggcaaacgagatattctgaatattggtgcatatttcaggtagaaaagcttacaaaacaatctaatcataatattgagatgaagagaaagataaaagaaaaaacgataagtcagatgagattatgattgtactttgaaatcgaggaacaaagtatatacggtagtagttccccgagttataacgggagatcatgtaaattgagaaaccagataaagatttggtatgcactctagcaagaaaataaaatgatgaatctatgatatagatcacttttgttccagcatccggatttacctgaatcaattggcgaaattttttgtacgaaatttcagccacttcacag
   
    >5681
    atccggatttacctgaatcaattggcgaaattttttgtacgaaatttcagccacttcacaggcggttttcgcacgtacccatgcgctacgttcctggccctcttcaaacaggcccagttcgccaataaaatcaccctgattcagataggagaggatcatttctttaccctcttcgtctttgatcagcactgccacagagcctttaacgatgtagtacagcgtttccgctttttcaccctggtgaataagcgtgctcttggatgggtacttatgaatgtggcaatgagacaagaaccattcgagagtaggatccgtttgaggtttaccaagtaccataagatccttaaatttttattatctagctagatgataatattatatcaagaattgtacctgaaagcaaataaattttttatctggcttaactatgcggcatcagagcagattgtactgagagtgcaccatatgcggtgtgaaataccgcacagatgcgtaaggagaaaataccgcatcaggcgctcttccgcttcctcgctcactgactcgctgcgctcggtcgttcggctgcggcgagcggtatcagctcactcaaaggcggtaatacggttatccacagaatcaggggataacgcaggaaagaacatgtgagcaaaaggccagcaaaagcccaggaaccgtaaaaaggccgcgttgctggcgtttttccataggctccgcccccctgacgagcatcacaaaaatcgacgctcaagtcagaggtggcgaaacccgacaggactataaagataccaggcgtttccccctggaagctccctcgtgcgctctcctgttccgaccctgccgcttaccggatacctgtccgcctttctcccttcgggaagcgtggcgctttctcatagctcacgctgtaggtatctcagttcggtgtaggtcgttcgctccaagctgggctgtgtgcacgaaccccccgttcagcccgaccgctgcgccttatccggtaactatcgtcttgagtccaacccggtaagacacgacttatcgccactggcagcagccactggtaacaggattagcagagcgaggtatgtaggcggtgctacagagttcttgaagtggtggcctaactacggctacactagaaggacagtatttggtatctgcgctctgctgaagccagttaccttcggaaaaagagttggtagctcttgatccggcaaacaaaccaccgctggtagcggtggtttttttgtttgcaagcagcagattacgcgcagaaaaaaaggatctcaagaagatcctttgatcttttctacggggtctgacgctcagtggaacgaaaactcacgttaagggattttggtcatgaggggtaataactgatataattaaattgaagctctaatttgtgagtttagtatacatgcatttacttataatacagttttttagttttgctggccgcatcttctcaaatatgcttcccagcctgcttttctgtaacgttcaccctctaccttagcatcccttccctttgcaaatagtcctcttccaacaataataatgtcagatcctgtagagaccacatcatccacggttctatactgttgacccaatgcgtctcccttgtcatctaaacccacaccgggtgtcataatcaaccaatcgtaaccttcatctcttccacccatgtctctttgagcaataaagccgataacaaaatctttgtcgctcttcgcaatgtcaacagtacccttagtatattctccagtagatagggagcccttgcatgacaattctgctaacatcaaaaggcctctaggttcctttgttacttcttctgccgcctgcttcaaaccgctaacaatacctgggcccaccacaccgtgtgcattcgtaatgtctgcccattctgctattctgtatacacccgcagagtactgcaatttgactgtattaccaatgtcagcaaattttctgtcttcgaagagtaaaaaattgtacttggcggataatgcctttagcggcttaactgtgccctccatggaaaaatcagtcaaaatatccacatgtgtttttagtaaacaaattttgggacctaatgcttcaactaactccagtaattccttggtggtacgaacatccaatgaagcacacaagtttgtttgcttttcgtgcatgatattaaatagcttggcagcaacaggactaggatgagtagcagcacgttccttatatgtagctttcgacatgatttatcttcgtttcctgcaggtttttgttctgtgcagttgggttaagaatactgggcaatttcatgtttcttcaacactacatatgcgtatatataccaatctaagtctgtgctccttccttcgttcttccttctgttcggagattaccgaatcaaaaaaatttcaaagaaaccgaaatcaaaaaaaagaataaaaaaaaaatgatgaattgaattgaaaagctagcttatcgatgataagctgtcaaagatgagaattaattccacggactatagactatactagatactccgtctactgtacgatacacttccgctcaggtccttgtcctttaacgaggccttaccactcttttgttactctattgatccagctcagcaaaggcagtgtgatctaagattctatcttcgcgatgtagtaaaactagctagaccgagaaagagactagaaatgcaaaaggcacttctacaatggctgccatcattattatccgatgtgacgctgcagcttctcaatgatattcgaatacgctttgaggagatacagcctaatatccgacaaactgttttacagatttacgatcgtacttgttacccatcattgaattttgaacatccgaacctgggagttttccctgaaacagatagtatatttgaacctgtataataatatatagtctagcgctttacggaagacaatgtatgtatttcggttcctggagaaactattgcatctattgcataggtaatcttgcacgtcgcatccccggttcattttctgcgtttccatcttgcacttcaatagcatatctttgttaacgaagcatctgtgcttcattttgtagaacaaaaatgcaacgcgagagcgctaatttttcaaacaaagaatctgagctgcatttttacagaacagaaatgcaacgcgaaagcgctattttaccaacgaagaatctgtgcttcatttttgtaaaacaaaaatgcaacgcgacgagagcgctaatttttcaaacaaagaatctgagctgcatttttacagaacagaaatgcaacgcgagagcgctattttaccaacaaagaatctatacttcttttttgttctacaaaaatgcatcccgagagcgctatttttctaacaaagcatcttagattactttttttctcctttgtgcgctctataatgcagtctcttgataactttttgcactgtaggtccgttaaggttagaagaaggctactttggtgtctattttctcttccataaaaaaagcctgactccacttcccgcgtttactgattactagcgaagctgcgggtgcattttttcaagataaaggcatccccgattatattctataccgatgtggattgcgcatactttgtgaacagaaagtgatagcgttgatgattcttcattggtcagaaaattatgaacggtttcttctattttgtctctatatactacgtataggaaatgtttacattttcgtattgttttcgattcactctatgaatagttcttactacaatttttttgtctaaagagtaatactagagataaacataaaaaatgtagaggtcgagtttagatgcaagttcaaggagcgaaaggtggatgggtaggttatatagggatatagcacagagatatatagcaaagagatacttttgagcaatgtttgtggaagcggtattcgcaatgggaagctccaccccggttgataatcagaaaagccccaaaaacaggaagattattatcaaaaaggatcttcacctagatccttttaaattaaaaatgaagttttaaatcaatctaaagtatatatgagtaaacttggtctgacagttaccaatgcttaatcagtgaggcacctatctcagcgatctgtctatttcgttcatccatagttgcctgactccccgtcgtgtagataactacgatacgggagcgcttaccatctggccccagtgctgcaatgataccgcgagacccacgctcaccggctccagatttatcagcaataaaccagccagccggaagggccgagcgcagaagtggtcctgcaactttatccgcctccatccagtctattaattgttgccgggaagctagagtaagtagttcgccagttaatagtttgcgcaacgttgttggcattgctacaggcatcgtggtgtcactctcgtcgtttggtatggcttcattcagctccggttcccaacgatcaaggcgagttacatgatcccccatgttgtgcaaaaaagcggttagctccttcggtcctccgatcgttgtcagaagtaagttggccgcagtgttatcactcatggttatggcagcactgcataattctcttactgtcatgccatccgtaagatgcttttctgtgactggtgagtactcaaccaagtcattctgagaatagtgtatgcggcgaccgagttgctcttgcccggcgtcaatacgggataatagtgtatcacatagcagaactttaaaagtgctcatcattggaaaacgttcttcggggcgaaaactctcaaggatcttaccgctgttgagatccagttcgatgtaacccactcgtgcacccaactgatcttcagcatcttttactttcaccagcgtttctgggtgagcaaaaacaggaaggcaaaatgccgcaaaaaagggaataagggcgacacggaaatgttgaatactcatactcttcctttttcaatattattgaagcatttatcagggttattgtctcatgagcggatacatatttgaatgtatttagaaaaataaacaaataggggttccgcgcacatttccccgaaaagtgccacctgctaagaaaccattattatcatgacattaacctataaaaataggcgtatcacgaggccctttcgtctcgcgcgtttcggtgatgacggtgaaaacctctgacacatgcagctcccggagacggtcacagcttgtctgtaagcggatgccgggagcagacaagcccgtcagggcgcgtcagcgggtgttggcgggtgtcggggctggcttaactatgcggcatcagagcagattgtactgagagtgcaccatagatcctgaggatcggggtgataaatcagtctgcgccacatcgggggaaacaaaatggcgcgagatctaaaaaaaaaggctccaaaaggagcctttcgcgctaccaggtaacgcgccactccgacgggattaacgagtgccgtaaacgacgatggttttaccgtgtgcggagatcaggttctgatcctcgagcatcttaagaattcgtcccacggtttgtctagagcagccgacaatctggccaatttcctgacgggtaattttgatttgcatgccgtccgggtgagtcatagcgtctggttgttttgccagattcagcagagtctgtgcaatgcggccgctgac
    
    '''
    
    
    lst = parse(text5)
    prods = recombination_assembly(lst, limit=60)
    correct = 'tcgcgcgtttcggtgatgacggtgaaaacctctgacacatgcagctcccggagacggtcacagcttgtctgtaagcggatgccgggagcagacaagcccgtcagggcgcgtcagcgggtgttggcgggtgtcggggctggcttaactatgcggcatcagagcagattgtactgagagtgcaccatagatcctgaggatcggggtgataaatcagtctgcgccacatcgggggaaacaaaatggcgcgagatctaaaaaaaaaggctccaaaaggagcctttcgcgctaccaggtaacgcgccactccgacgggattaacgagtgccgtaaacgacgatggttttaccgtgtgcggagatcaggttctgatcctcgagcatcttaagaattcgtcccacggtttgtctagagcagccgacaatctggccaatttcctgacgggtaattttgatttgcatgccgtccgggtgagtcatagcgtctggttgttttgccagattcagcagagtctgtgcaatgcggccgctgaccacatacgatttaggtgacactatagaacgcggccgccagctgaagcttcgtacgctgcaggtcgacggatccccgggttaattaaggcgcgccagatctgtttagcttgccttgtccccgccgggtcacccggccagcgacatggaggcccagaataccctccttgacagtcttgacgtgcgcagctcaggggcatgatgtgactgtcgcccgtacatttagcccatacatccccatgtataatcatttgcatccatacattttgatggccgcacggcgcgaagcaaaaattacggctcctcgctgcagacctgcgagcagggaaacgctcccctcacagacgcgttgaattgtccccacgccgcgcccctgtagagaaatataaaaggttaggatttgccactgaggttcttctttcatatacttccttttaaaatcttgctaggatacagttctcacatcacatccgaacataaacaaccgtcgaggaacgccaggttgcccactttctcactagtgacctgcagccgacccaatcacatcacatccgaacataaacaaccatgggtaaaaagcctgaactcaccgcgacgtctgtcgagaagtttctgatcgaaaagttcgacagcgtctccgacctgatgcagctctcggagggcgaagaatctcgtgctttcagcttcgatgtaggagggcgtggatatgtcctgcgggtaaatagctgcgccgatggtttctacaaagatcgttatgtttatcggcactttgcatcggccgcgctcccgattccggaagtgcttgacattggggaattcagcgagagcctgacctattgcatctcccgccgtgcacagggtgtcacgttgcaagacctgcctgaaaccgaactgcccgctgttctgcagccggtcgcggaggccatggatgcgatcgctgcggccgatcttagccagacgagcgggttcggcccattcggaccgcaaggaatcggtcaatacactacatggcgtgatttcatatgcgcgattgctgatccccatgtgtatcactggcaaactgtgatggacgacaccgtcagtgcgtccgtcgcgcaggctctcgatgagctgatgctttgggccgaggactgccccgaagtccggcacctcgtgcacgcggatttcggctccaacaatgtcctgacggacaatggccgcataacagcggtcattgactggagcgaggcgatgttcggggattcccaatacgaggtcgccaacatcttcttctggaggccgtggttggcttgtatggagcagcagacgcgctacttcgagcggaggcatccggagcttgcaggatcgccgcggctccgggcgtatatgctccgcattggtcttgaccaactctatcagagcttggttgacggcaatttcgatgatgcagcttgggcgcagggtcgatgcgacgcaatcgtccgatccggagccgggactgtcgggcgtacacaaatcgcccgcagaagcgcggccgtctggaccgatggctgtgtagaagtactcgccgatagtggaaaccgacgccccagcactcgtccgagggcaaaggaataatcagtactgacaataaaaagattcttgtagggataacagggtaatcggagtgccatctgtgcagacaaacgcatcaggatagagtcttttgtaacgaccccgtctccaccaacttggtatgcttgaaatctcaaggccattacacattcagttatgtgaacgaaaggtctttatttaacgtagcataaactaaataatacaggttccggttagcctgcaatgtgttaaatctaaaggagcatacccaaaatgaactgaagacaaggaaatttgcttgtccagatgtgattgagcatttgaacgttaataacataacatttttatacttaactatagaaagacttgtataaaaactggcaaacgagatattctgaatattggtgcatatttcaggtagaaaagcttacaaaacaatctaatcataatattgagatgaagagaaagataaaagaaaaaacgataagtcagatgagattatgattgtactttgaaatcgaggaacaaagtatatacggtagtagttccccgagttataacgggagatcatgtaaattgagaaaccagataaagatttggtatgcactctagcaagaaaataaaatgatgaatctatgatatagatcacttttgttccagcgtcgaggaacgccaggttgcccactttctcactagtgacctgcagccgacgatcagatctttcaggaaagtttcggaggagatagtgttcggcagtttgtacatcatctgcgggatcaggtacggtttgatcaggttgtagaagatcaggtaagacatagaatcgatgtagatgatcggtttgtttttgttgatttttacgtaacagttcagttggaatttgttacgcagacccttaaccaggtattctacttcttcgaaagtgaaagactgggtgttcagtacgatcgatttgttggtagagtttttgttgtaatcccatttaccaccatcatccatgaaccagtatgccagagacatcggggtcaggtagttttcaaccaggttgttcgggatggtttttttgttgttaacgatgaacaggttagccagtttgttgaaagcttggtgtttgaaagtctgggcgccccaggtgattaccaggttacccaggtggttaacacgttcttttttgtgcggcggggacagtacccactgatcgtacagcagacatacgtggtccatgtatgctttgtttttccactcgaactgcatacagtaggttttaccttcatcacgagaacggatgtaagcatcacccaggatcagaccgatacctgcttcgaactgttcgatgttcagttcgatcagctgggatttgtattctttcagcagtttagagttcggacccaggttcattacctggttttttttgatgtttttcatatgcatggatccggggttttttctccttgacgttaaagtatagaggtatattaacaattttttgttgatacttttattacatttgaataagaagtaatacaaaccgaaaatgttgaaagtattagttaaagtggttatgcagtttttgcatttatatatctgttaatagatcaaaaatcatcgcttcgctgattaattaccccagaaataaggctaaaaaactaatcgcattatcatcctatggttgttaatttgattcgttcatttgaaggtttgtggggccaggttactgccaatttttcctcttcataaccataaaagctagtattgtagaatctttattgttcggagcagtgcggcgcgaggcacatctgcgtttcaggaacgcgaccggtgaagacgaggacgcacggaggagagtcttccttcggagggctgtcacccgctcggcggcttctaatccgtacttcaatatagcaatgagcagttaagcgtattactgaaagttccaaagagaaggtttttttaggctaagataatggggctctttacatttccacaacatataagtaagattagatatggatatgtatatggatatgtatatggtggtaatgccatgtaatatgattattaaacttctttgcgtccatccaacgagatctggcgcgccttaattaacccaacctgcattaatgaatcggccaacgcgcggattaccctgttatccctacatattgttgtgccatctgtgcagacaaacgcatcaggattcagtactgacaataaaaagattcttgttttcaagaacttgtcatttgtatagtttttttatattgtagttgttctattttaatcaaatgttagcgtgatttatattttttttcgcctcgacatcatctgcccagatgcgaagttaagtgcgcagaaagtaatatcatgcgtcaatcgtatgtgaatgctggtcgctatactgctgtcgattcgatactaacgccgccatccagtgtcgaaaacgagctcgaattcatcgatgatatcagatccactagtggcctatgcggccgcggatctgccggtctccctatagtgagtcgatccggatttacctgaatcaattggcgaaattttttgtacgaaatttcagccacttcacaggcggttttcgcacgtacccatgcgctacgttcctggccctcttcaaacaggcccagttcgccaataaaatcaccctgattcagataggagaggatcatttctttaccctcttcgtctttgatcagcactgccacagagcctttaacgatgtagtacagcgtttccgctttttcaccctggtgaataagcgtgctcttggatgggtacttatgaatgtggcaatgagacaagaaccattcgagagtaggatccgtttgaggtttaccaagtaccataagatccttaaatttttattatctagctagatgataatattatatcaagaattgtacctgaaagcaaataaattttttatctggcttaactatgcggcatcagagcagattgtactgagagtgcaccatatgcggtgtgaaataccgcacagatgcgtaaggagaaaataccgcatcaggcgctcttccgcttcctcgctcactgactcgctgcgctcggtcgttcggctgcggcgagcggtatcagctcactcaaaggcggtaatacggttatccacagaatcaggggataacgcaggaaagaacatgtgagcaaaaggccagcaaaagcccaggaaccgtaaaaaggccgcgttgctggcgtttttccataggctccgcccccctgacgagcatcacaaaaatcgacgctcaagtcagaggtggcgaaacccgacaggactataaagataccaggcgtttccccctggaagctccctcgtgcgctctcctgttccgaccctgccgcttaccggatacctgtccgcctttctcccttcgggaagcgtggcgctttctcatagctcacgctgtaggtatctcagttcggtgtaggtcgttcgctccaagctgggctgtgtgcacgaaccccccgttcagcccgaccgctgcgccttatccggtaactatcgtcttgagtccaacccggtaagacacgacttatcgccactggcagcagccactggtaacaggattagcagagcgaggtatgtaggcggtgctacagagttcttgaagtggtggcctaactacggctacactagaaggacagtatttggtatctgcgctctgctgaagccagttaccttcggaaaaagagttggtagctcttgatccggcaaacaaaccaccgctggtagcggtggtttttttgtttgcaagcagcagattacgcgcagaaaaaaaggatctcaagaagatcctttgatcttttctacggggtctgacgctcagtggaacgaaaactcacgttaagggattttggtcatgaggggtaataactgatataattaaattgaagctctaatttgtgagtttagtatacatgcatttacttataatacagttttttagttttgctggccgcatcttctcaaatatgcttcccagcctgcttttctgtaacgttcaccctctaccttagcatcccttccctttgcaaatagtcctcttccaacaataataatgtcagatcctgtagagaccacatcatccacggttctatactgttgacccaatgcgtctcccttgtcatctaaacccacaccgggtgtcataatcaaccaatcgtaaccttcatctcttccacccatgtctctttgagcaataaagccgataacaaaatctttgtcgctcttcgcaatgtcaacagtacccttagtatattctccagtagatagggagcccttgcatgacaattctgctaacatcaaaaggcctctaggttcctttgttacttcttctgccgcctgcttcaaaccgctaacaatacctgggcccaccacaccgtgtgcattcgtaatgtctgcccattctgctattctgtatacacccgcagagtactgcaatttgactgtattaccaatgtcagcaaattttctgtcttcgaagagtaaaaaattgtacttggcggataatgcctttagcggcttaactgtgccctccatggaaaaatcagtcaaaatatccacatgtgtttttagtaaacaaattttgggacctaatgcttcaactaactccagtaattccttggtggtacgaacatccaatgaagcacacaagtttgtttgcttttcgtgcatgatattaaatagcttggcagcaacaggactaggatgagtagcagcacgttccttatatgtagctttcgacatgatttatcttcgtttcctgcaggtttttgttctgtgcagttgggttaagaatactgggcaatttcatgtttcttcaacactacatatgcgtatatataccaatctaagtctgtgctccttccttcgttcttccttctgttcggagattaccgaatcaaaaaaatttcaaagaaaccgaaatcaaaaaaaagaataaaaaaaaaatgatgaattgaattgaaaagctagcttatcgatgataagctgtcaaagatgagaattaattccacggactatagactatactagatactccgtctactgtacgatacacttccgctcaggtccttgtcctttaacgaggccttaccactcttttgttactctattgatccagctcagcaaaggcagtgtgatctaagattctatcttcgcgatgtagtaaaactagctagaccgagaaagagactagaaatgcaaaaggcacttctacaatggctgccatcattattatccgatgtgacgctgcagcttctcaatgatattcgaatacgctttgaggagatacagcctaatatccgacaaactgttttacagatttacgatcgtacttgttacccatcattgaattttgaacatccgaacctgggagttttccctgaaacagatagtatatttgaacctgtataataatatatagtctagcgctttacggaagacaatgtatgtatttcggttcctggagaaactattgcatctattgcataggtaatcttgcacgtcgcatccccggttcattttctgcgtttccatcttgcacttcaatagcatatctttgttaacgaagcatctgtgcttcattttgtagaacaaaaatgcaacgcgagagcgctaatttttcaaacaaagaatctgagctgcatttttacagaacagaaatgcaacgcgaaagcgctattttaccaacgaagaatctgtgcttcatttttgtaaaacaaaaatgcaacgcgacgagagcgctaatttttcaaacaaagaatctgagctgcatttttacagaacagaaatgcaacgcgagagcgctattttaccaacaaagaatctatacttcttttttgttctacaaaaatgcatcccgagagcgctatttttctaacaaagcatcttagattactttttttctcctttgtgcgctctataatgcagtctcttgataactttttgcactgtaggtccgttaaggttagaagaaggctactttggtgtctattttctcttccataaaaaaagcctgactccacttcccgcgtttactgattactagcgaagctgcgggtgcattttttcaagataaaggcatccccgattatattctataccgatgtggattgcgcatactttgtgaacagaaagtgatagcgttgatgattcttcattggtcagaaaattatgaacggtttcttctattttgtctctatatactacgtataggaaatgtttacattttcgtattgttttcgattcactctatgaatagttcttactacaatttttttgtctaaagagtaatactagagataaacataaaaaatgtagaggtcgagtttagatgcaagttcaaggagcgaaaggtggatgggtaggttatatagggatatagcacagagatatatagcaaagagatacttttgagcaatgtttgtggaagcggtattcgcaatgggaagctccaccccggttgataatcagaaaagccccaaaaacaggaagattattatcaaaaaggatcttcacctagatccttttaaattaaaaatgaagttttaaatcaatctaaagtatatatgagtaaacttggtctgacagttaccaatgcttaatcagtgaggcacctatctcagcgatctgtctatttcgttcatccatagttgcctgactccccgtcgtgtagataactacgatacgggagcgcttaccatctggccccagtgctgcaatgataccgcgagacccacgctcaccggctccagatttatcagcaataaaccagccagccggaagggccgagcgcagaagtggtcctgcaactttatccgcctccatccagtctattaattgttgccgggaagctagagtaagtagttcgccagttaatagtttgcgcaacgttgttggcattgctacaggcatcgtggtgtcactctcgtcgtttggtatggcttcattcagctccggttcccaacgatcaaggcgagttacatgatcccccatgttgtgcaaaaaagcggttagctccttcggtcctccgatcgttgtcagaagtaagttggccgcagtgttatcactcatggttatggcagcactgcataattctcttactgtcatgccatccgtaagatgcttttctgtgactggtgagtactcaaccaagtcattctgagaatagtgtatgcggcgaccgagttgctcttgcccggcgtcaatacgggataatagtgtatcacatagcagaactttaaaagtgctcatcattggaaaacgttcttcggggcgaaaactctcaaggatcttaccgctgttgagatccagttcgatgtaacccactcgtgcacccaactgatcttcagcatcttttactttcaccagcgtttctgggtgagcaaaaacaggaaggcaaaatgccgcaaaaaagggaataagggcgacacggaaatgttgaatactcatactcttcctttttcaatattattgaagcatttatcagggttattgtctcatgagcggatacatatttgaatgtatttagaaaaataaacaaataggggttccgcgcacatttccccgaaaagtgccacctgctaagaaaccattattatcatgacattaacctataaaaataggcgtatcacgaggccctttcgtc'
    
    assert eq(correct,prods.circular[0].result, circular=True)
    
    print prods.circular[0].overlap_sizes
    
    import time
    for p in prods.circular[0].sticky_fragments:
        ape(p)
        time.sleep(1)
    
    
    for x in prods.linear:
        print len(x.result)

    
#    for seq, spc in zip(prods.circular[0].sticky_fragments, prods.circular[0].sticky_alignments):
#        print " "*spc+str(seq.seq)
#    for seq, spc in zip(prods.circular[0].source_fragments, prods.circular[0].source_alignments):
#        print " "*spc+str(seq.seq)
    

'''


sticky

s    e        s     e
1    1        2     2
|    |        |     |
      <------>
%abA%%--2479--!!OmD!!                          
                     <-------------->
              !!OmD!!---5681---------=pX1=
                                          <------>
                                     =pX1=--2389--%%abA%%
<------------>



      s    e        s     e
      1    1        2     2
      |    |        |     |
            <------>
=pX1=%%abA%%--2577--!!OmD!!                          
                           <-------------->
            --------!!OmD!!---5681---------=pX1=
                                                <------>
                                           =pX1=--2389--%%abA%%!!OmD!!



sticky
0    (2479)
2418 (5681)
8001 (2389)


source
0    (2479)
2516 (5681)
8099 (2389)

'''


#    import subprocess
    
#    import tempfile, os
#    with tempfile.NamedTemporaryFile() as temp:
#        temp.write('Some data')
#        temp.flush()
#        temp.seek(0)
#        print temp.name, os.path.isfile(temp.name)
#        print temp.read()
#        print "gedit {}".format(temp.name)
#        p = subprocess.Popen( "gedit {}".format(temp.name) )
    
